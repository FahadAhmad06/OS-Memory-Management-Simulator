"""Entry point for the OS Memory Management Simulator (OS-MMS) Python CustomTkinter GUI."""

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import messagebox
from typing import Dict, Tuple

# Ensure `frontend/` is on sys.path regardless of current working directory
FRONTEND_ROOT = Path(__file__).resolve().parent
if str(FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(FRONTEND_ROOT))

import customtkinter as ctk  # noqa: E402

from backend_bridge import BackendBridge  # noqa: E402
from components.header import HeaderBar  # noqa: E402
from components.sidebar import Sidebar  # noqa: E402
from config import (  # noqa: E402
    APP_SUBTITLE,
    APP_TITLE,
    COLORS,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from pages.about import AboutPage  # noqa: E402
from pages.comparison import ComparisonPage  # noqa: E402
from pages.home import HomePage  # noqa: E402
from pages.memory_allocation import MemoryAllocationPage  # noqa: E402
from pages.page_replacement import PageReplacementPage  # noqa: E402
from pages.paging import PagingPage  # noqa: E402


PAGE_METADATA: Dict[str, Tuple[str, str]] = {
    "home": (APP_TITLE, APP_SUBTITLE),
    "memory_allocation": (
        "Contiguous Memory Allocation",
        "Simulate First Fit, Best Fit, and Worst Fit partition placement",
    ),
    "paging": (
        "Paging & Address Translation",
        "Decompose logical addresses and translate via page tables to physical frames",
    ),
    "page_replacement": (
        "Page Replacement Algorithms",
        "Trace FIFO, LRU, and Optimal frame states, hits, and page faults",
    ),
    "comparison": (
        "Algorithm Performance Comparison",
        "Benchmark Memory Allocation and Page Replacement strategies on identical inputs",
    ),
    "about": (
        "About OS-MMS",
        "Project overview, technical stack, and BSCS team at UVAS Lahore",
    ),
}


class OSMemorySimulatorApp(ctk.CTk):
    """Main application window coordinating navigation, shared backend bridge, and safe shutdown."""

    def __init__(self) -> None:
        super().__init__()

        # Enforce strictly Light Mode theme
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_TITLE} — UVAS Lahore")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.configure(fg_color=COLORS["app_bg"])

        self.bridge = BackendBridge()
        self._pages: Dict[str, ctk.CTkFrame] = {}
        self._current_page_key: str = ""

        self._build_shell()
        self._refresh_backend_status()
        self.navigate("home")

        self.protocol("WM_DELETE_WINDOW", self.confirm_and_exit)

    def _build_shell(self) -> None:
        # Permanent left sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self.navigate,
            on_exit=self.confirm_and_exit,
        )
        self.sidebar.pack(side="left", fill="y")

        # Right workspace area (Header + Central Scrollable Viewport)
        right_shell = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        right_shell.pack(side="right", fill="both", expand=True)

        self.header = HeaderBar(
            right_shell,
            on_refresh_status=self._refresh_backend_status,
        )
        self.header.pack(side="top", fill="x")

        self.scroll_viewport = ctk.CTkScrollableFrame(
            right_shell,
            fg_color=COLORS["content_bg"],
            corner_radius=0,
        )
        self.scroll_viewport.pack(side="top", fill="both", expand=True, padx=18, pady=16)

        # Instantiate all six application pages inside the scrollable viewport
        self._pages = {
            "home": HomePage(self.scroll_viewport, on_navigate=self.navigate),
            "memory_allocation": MemoryAllocationPage(self.scroll_viewport, bridge=self.bridge),
            "paging": PagingPage(self.scroll_viewport, bridge=self.bridge),
            "page_replacement": PageReplacementPage(self.scroll_viewport, bridge=self.bridge),
            "comparison": ComparisonPage(self.scroll_viewport, bridge=self.bridge),
            "about": AboutPage(self.scroll_viewport),
        }

    def _refresh_backend_status(self) -> None:
        status = self.bridge.get_executable_status()
        self.header.set_backend_status(
            available=bool(status["available"]),
            message=str(status["message"]),
        )

    def navigate(self, page_key: str) -> None:
        if page_key not in self._pages:
            return
        if self._current_page_key == page_key:
            return

        for key, frame in self._pages.items():
            if key == page_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        self._current_page_key = page_key
        self.sidebar.set_active(page_key)
        title, subtitle = PAGE_METADATA.get(page_key, (APP_TITLE, APP_SUBTITLE))
        self.header.set_page_info(title, subtitle)

        # Scroll viewport back to top on page change
        try:
            self.scroll_viewport._parent_canvas.yview_moveto(0.0)
        except Exception:  # noqa: BLE001
            pass

    def confirm_and_exit(self) -> None:
        should_exit = messagebox.askyesno(
            title="Exit OS Memory Management Simulator",
            message="Are you sure you want to close the OS Memory Management Simulator?",
            icon="question",
        )
        if not should_exit:
            return

        self.bridge.cleanup()
        try:
            self.quit()
        finally:
            self.destroy()


def main() -> None:
    app = OSMemorySimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
