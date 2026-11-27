"""Styled CustomTkinter buttons adhering to the light blue & white theme."""

from __future__ import annotations

from typing import Any, Callable, Optional
import customtkinter as ctk

from config import COLORS, CORNER_RADIUS_BTN, FONTS


class PrimaryButton(ctk.CTkButton):
    """Primary blue action button."""

    def __init__(
        self,
        master: Any,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 140,
        height: int = 38,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=CORNER_RADIUS_BTN,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_on_primary"],
            font=FONTS["body_bold"],
            **kwargs,
        )


class SecondaryButton(ctk.CTkButton):
    """Soft blue secondary action button."""

    def __init__(
        self,
        master: Any,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 140,
        height: int = 38,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=CORNER_RADIUS_BTN,
            fg_color=COLORS["primary_soft"],
            hover_color=COLORS["primary_light"],
            text_color=COLORS["primary"],
            border_width=1,
            border_color=COLORS["border_strong"],
            font=FONTS["body_bold"],
            **kwargs,
        )


class NeutralButton(ctk.CTkButton):
    """Subtle neutral reset/clear button."""

    def __init__(
        self,
        master: Any,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 110,
        height: int = 38,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=CORNER_RADIUS_BTN,
            fg_color=COLORS["neutral_btn"],
            hover_color=COLORS["neutral_btn_hover"],
            text_color=COLORS["neutral_btn_text"],
            font=FONTS["body_bold"],
            **kwargs,
        )


class DangerButton(ctk.CTkButton):
    """Destructive / remove action button."""

    def __init__(
        self,
        master: Any,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 110,
        height: int = 34,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=CORNER_RADIUS_BTN,
            fg_color=COLORS["danger_bg"],
            hover_color=COLORS["danger_border"],
            text_color=COLORS["danger"],
            border_width=1,
            border_color=COLORS["danger_border"],
            font=FONTS["small_bold"],
            **kwargs,
        )
