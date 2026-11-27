"""Top navigation header displaying active page title, subtitle, and C++ backend status badge."""

from __future__ import annotations

from typing import Any, Callable
import customtkinter as ctk

from config import COLORS, FONTS, HEADER_HEIGHT


class HeaderBar(ctk.CTkFrame):
    """Top header bar spanning the workspace above the central scrollable viewport."""

    def __init__(
        self,
        master: Any,
        on_refresh_status: Callable[[], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            height=HEADER_HEIGHT,
            fg_color=COLORS["header_bg"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.pack_propagate(False)
        self._on_refresh_status = on_refresh_status

        left_box = ctk.CTkFrame(self, fg_color="transparent")
        left_box.pack(side="left", fill="y", padx=20)

        self.title_label = ctk.CTkLabel(
            left_box,
            text="OS Memory Management Simulator",
            font=FONTS["page_title"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.title_label.pack(anchor="w", pady=(12, 0))

        self.subtitle_label = ctk.CTkLabel(
            left_box,
            text="Visualize, Analyze, Understand",
            font=FONTS["subtitle"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self.subtitle_label.pack(anchor="w", pady=(0, 8))

        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.pack(side="right", fill="y", padx=20)

        status_row = ctk.CTkFrame(right_box, fg_color="transparent")
        status_row.pack(anchor="e", pady=18)

        self.status_badge = ctk.CTkLabel(
            status_row,
            text="Checking C++ Backend...",
            font=FONTS["small_bold"],
            fg_color=COLORS["info_bg"],
            text_color=COLORS["info"],
            corner_radius=8,
            padx=12,
            pady=6,
        )
        self.status_badge.pack(side="left", padx=(0, 8))

        self.refresh_btn = ctk.CTkButton(
            status_row,
            text="↻",
            width=34,
            height=32,
            corner_radius=8,
            fg_color=COLORS["primary_soft"],
            hover_color=COLORS["primary_light"],
            text_color=COLORS["primary"],
            font=FONTS["body_bold"],
            command=self._on_refresh_status,
        )
        self.refresh_btn.pack(side="left")

    def set_page_info(self, title: str, subtitle: str) -> None:
        self.title_label.configure(text=title)
        self.subtitle_label.configure(text=subtitle)

    def set_backend_status(self, available: bool, message: str) -> None:
        if available:
            self.status_badge.configure(
                text=f"●  {message}",
                fg_color=COLORS["success_bg"],
                text_color=COLORS["success"],
            )
        else:
            self.status_badge.configure(
                text=f"▲  {message}",
                fg_color=COLORS["danger_bg"],
                text_color=COLORS["danger"],
            )
