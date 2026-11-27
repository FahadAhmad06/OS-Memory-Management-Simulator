"""Reusable white card containers, KPI metric cards, and status banners."""

from __future__ import annotations

from typing import Any, Optional
import customtkinter as ctk

from config import COLORS, CORNER_RADIUS_CARD, FONTS


class CardFrame(ctk.CTkFrame):
    """Standard rounded white card with crisp light-blue border."""

    def __init__(
        self,
        master: Any,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        fg_color: str = COLORS["card_bg"],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color=fg_color,
            corner_radius=CORNER_RADIUS_CARD,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.header_frame: Optional[ctk.CTkFrame] = None
        if title:
            self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.header_frame.pack(fill="x", padx=16, pady=(14, 6))

            title_lbl = ctk.CTkLabel(
                self.header_frame,
                text=title,
                font=FONTS["card_title"],
                text_color=COLORS["text_primary"],
                anchor="w",
            )
            title_lbl.pack(side="left")

            if subtitle:
                sub_lbl = ctk.CTkLabel(
                    self.header_frame,
                    text=subtitle,
                    font=FONTS["small"],
                    text_color=COLORS["text_muted"],
                    anchor="e",
                )
                sub_lbl.pack(side="right")


class MetricCard(ctk.CTkFrame):
    """Compact KPI statistic card displaying a title, primary value, and helper note."""

    def __init__(
        self,
        master: Any,
        label: str,
        initial_value: str = "—",
        accent_color: str = COLORS["primary"],
        subtext: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color=COLORS["card_bg"],
            corner_radius=CORNER_RADIUS_CARD,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._accent = ctk.CTkFrame(
            self,
            height=4,
            fg_color=accent_color,
            corner_radius=2,
        )
        self._accent.pack(fill="x", padx=14, pady=(10, 8))

        self.label_widget = ctk.CTkLabel(
            self,
            text=label.upper(),
            font=FONTS["metric_label"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self.label_widget.pack(fill="x", padx=14)

        self.value_widget = ctk.CTkLabel(
            self,
            text=initial_value,
            font=FONTS["metric_value"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.value_widget.pack(fill="x", padx=14, pady=(2, 2))

        self.subtext_widget = ctk.CTkLabel(
            self,
            text=subtext,
            font=FONTS["caption"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.subtext_widget.pack(fill="x", padx=14, pady=(0, 10))

    def set_value(self, value: str, subtext: Optional[str] = None, accent_color: Optional[str] = None) -> None:
        self.value_widget.configure(text=value)
        if subtext is not None:
            self.subtext_widget.configure(text=subtext)
        if accent_color is not None:
            self._accent.configure(fg_color=accent_color)


class StatusBanner(ctk.CTkFrame):
    """Inline notification banner for validation errors, backend errors, or run confirmations."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(
            master,
            fg_color=COLORS["info_bg"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["info_border"],
            **kwargs,
        )
        self._label = ctk.CTkLabel(
            self,
            text="",
            font=FONTS["small_bold"],
            text_color=COLORS["info"],
            anchor="w",
            wraplength=980,
            justify="left",
        )
        self._label.pack(fill="x", padx=14, pady=9)
        self._visible = False

    def show_info(self, message: str) -> None:
        self.configure(fg_color=COLORS["info_bg"], border_color=COLORS["info_border"])
        self._label.configure(text=f"ℹ  {message}", text_color=COLORS["info"])
        self._ensure_packed()

    def show_success(self, message: str) -> None:
        self.configure(fg_color=COLORS["success_bg"], border_color=COLORS["success_border"])
        self._label.configure(text=f"✓  {message}", text_color=COLORS["success"])
        self._ensure_packed()

    def show_error(self, message: str) -> None:
        self.configure(fg_color=COLORS["danger_bg"], border_color=COLORS["danger_border"])
        self._label.configure(text=f"✕  {message}", text_color=COLORS["danger"])
        self._ensure_packed()

    def hide(self) -> None:
        if self._visible:
            self.pack_forget()
            self._visible = False

    def _ensure_packed(self) -> None:
        if not self._visible:
            self.pack(fill="x", pady=(0, 12))
            self._visible = True
