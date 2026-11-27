"""Permanent left navigation sidebar with active blue highlight and safe exit trigger."""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

import customtkinter as ctk

from assets.icons.generator import create_nav_icon
from config import COLORS, FONTS, SIDEBAR_WIDTH


NAV_ITEMS: Tuple[Tuple[str, str, str], ...] = (
    ("home", "Home", "home"),
    ("memory_allocation", "Memory Allocation", "allocation"),
    ("paging", "Paging", "paging"),
    ("page_replacement", "Page Replacement", "replacement"),
    ("comparison", "Comparison", "comparison"),
    ("about", "About", "about"),
)


class Sidebar(ctk.CTkFrame):
    """Permanent left navigation sidebar."""

    def __init__(
        self,
        master: Any,
        on_navigate: Callable[[str], None],
        on_exit: Callable[[], None],
        **kwargs: Any,
    ) -> None:

        super().__init__(
            master,
            width=SIDEBAR_WIDTH,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

        self.pack_propagate(False)

        self._on_navigate = on_navigate
        self._on_exit = on_exit

        self._buttons: Dict[str, ctk.CTkButton] = {}
        self._active_icons: Dict[str, ctk.CTkImage] = {}
        self._inactive_icons: Dict[str, ctk.CTkImage] = {}

        self._active_key = ""

        self._build_brand()
        self._build_nav_items()
        self._build_footer()

    # --------------------------------------------------
    # BRAND SECTION
    # --------------------------------------------------

    def _build_brand(self) -> None:

        brand_box = ctk.CTkFrame(
            self,
            fg_color=COLORS["primary_soft"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border_strong"],
        )

        brand_box.pack(
            fill="x",
            padx=14,
            pady=(16, 14),
        )

        badge = ctk.CTkLabel(
            brand_box,
            text="OS-MMS",
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        )

        badge.pack(
            fill="x",
            padx=12,
            pady=(10, 0),
        )

        sub = ctk.CTkLabel(
            brand_box,
            text="Memory Management\nSimulator • UVAS Lahore",
            font=FONTS["caption"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            justify="left",
        )

        sub.pack(
            fill="x",
            padx=12,
            pady=(2, 10),
        )

        section_lbl = ctk.CTkLabel(
            self,
            text="NAVIGATION",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        )

        section_lbl.pack(
            fill="x",
            padx=18,
            pady=(4, 6),
        )

    # --------------------------------------------------
    # NAVIGATION ITEMS
    # --------------------------------------------------

    def _build_nav_items(self) -> None:

        nav_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        nav_container.pack(
            fill="x",
            padx=12,
        )

        for key, label, icon_name in NAV_ITEMS:

            # Active icon (white)
            self._active_icons[key] = create_nav_icon(
                icon_name,
                color="#FFFFFF",
                size=18,
            )

            # Inactive icon (blue)
            self._inactive_icons[key] = create_nav_icon(
                icon_name,
                color="#1D4ED8",
                size=18,
            )

            btn = ctk.CTkButton(
                nav_container,
                text=f"  {label}",
                image=self._inactive_icons[key],
                compound="left",
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=COLORS["primary_soft"],
                text_color=COLORS["text_primary"],
                font=FONTS["sidebar_item"],
                command=lambda k=key: self._on_navigate(k),
            )

            btn.pack(
                fill="x",
                pady=3,
            )

            self._buttons[key] = btn

    # --------------------------------------------------
    # FOOTER SECTION
    # --------------------------------------------------

    def _build_footer(self) -> None:

        spacer = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        spacer.pack(
            fill="both",
            expand=True,
        )

        divider = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS["divider"],
        )

        divider.pack(
            fill="x",
            padx=14,
            pady=(0, 10),
        )

        exit_icon = create_nav_icon(
            "exit",
            color="#B91C1C",
            size=18,
        )

        exit_btn = ctk.CTkButton(
            self,
            text="  Exit Application",
            image=exit_icon,
            compound="left",
            anchor="w",
            height=42,
            corner_radius=10,
            fg_color=COLORS["danger_bg"],
            hover_color=COLORS["danger_border"],
            text_color=COLORS["danger"],
            border_width=1,
            border_color=COLORS["danger_border"],
            font=FONTS["sidebar_item"],
            command=self._on_exit,
        )

        exit_btn.pack(
            fill="x",
            padx=12,
            pady=(0, 16),
        )

    # --------------------------------------------------
    # ACTIVE NAVIGATION HIGHLIGHT
    # --------------------------------------------------

    def set_active(self, page_key: str) -> None:
        """Update active navigation item."""

        if page_key not in self._buttons:
            raise ValueError(f"Invalid navigation page: {page_key}")

        self._active_key = page_key

        for key, btn in self._buttons.items():

            if key == page_key:

                # Active state
                btn.configure(
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"],
                    text_color=COLORS["text_on_primary"],
                    image=self._active_icons[key],
                )

            else:

                # Inactive state
                btn.configure(
                    fg_color="transparent",
                    hover_color=COLORS["primary_soft"],
                    text_color=COLORS["text_primary"],
                    image=self._inactive_icons[key],
                )

    # --------------------------------------------------
    # GET ACTIVE PAGE
    # --------------------------------------------------

    def get_active(self) -> str:
        """Return currently active navigation page."""

        return self._active_key
