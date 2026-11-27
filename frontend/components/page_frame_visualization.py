"""Frame-by-frame horizontal timeline visualizer for FIFO, LRU, and Optimal page replacement."""

from __future__ import annotations

from typing import Any, Dict, List
import customtkinter as ctk

from config import COLORS, FONTS


class PageFrameTimeline(ctk.CTkFrame):
    """
    Renders each reference step as a vertical column of frame slots with semantic highlights:
      - Hit: soft green highlight
      - Fault (newly loaded into empty frame): soft blue highlight
      - Fault (eviction / replacement): soft amber-red highlight with replaced page badge
    """

    def __init__(self, master: Any, compact: bool = False, **kwargs: Any) -> None:
        super().__init__(
            master,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._compact = compact
        self._build_header()

        self.scroll = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            height=190 if compact else 245,
            fg_color="transparent",
        )
        self.scroll.pack(fill="x", padx=10, pady=(0, 10))
        self._show_placeholder()

    def _build_header(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            bar,
            text="FRAME STATE TIMELINE",
            font=FONTS["small_bold"],
            text_color=COLORS["primary"],
        ).pack(side="left")

        legend = ctk.CTkFrame(bar, fg_color="transparent")
        legend.pack(side="right")

        items = [
            ("Hit", COLORS["success_bg"], COLORS["success"]),
            ("Fault (New Load)", COLORS["info_bg"], COLORS["info"]),
            ("Fault (Replaced)", COLORS["danger_bg"], COLORS["danger"]),
            ("Empty (-1)", COLORS["empty_frame_bg"], COLORS["empty_frame_text"]),
        ]
        for label, bg, fg in items:
            ctk.CTkLabel(
                legend,
                text=f" {label} ",
                font=FONTS["caption"],
                fg_color=bg,
                text_color=fg,
                corner_radius=6,
                padx=6,
                pady=2,
            ).pack(side="left", padx=3)

    def _show_placeholder(self) -> None:
        for child in self.scroll.winfo_children():
            child.destroy()
        ctk.CTkLabel(
            self.scroll,
            text="Run simulation to inspect frame-by-frame page hits, faults, and evictions.",
            font=FONTS["subtitle"],
            text_color=COLORS["text_muted"],
        ).pack(padx=20, pady=40)

    def clear(self) -> None:
        self._show_placeholder()

    def set_steps(self, frame_count: int, steps: List[Dict[str, Any]]) -> None:
        for child in self.scroll.winfo_children():
            child.destroy()

        if not steps or frame_count <= 0:
            self._show_placeholder()
            return

        col_w = 64 if self._compact else 76

        # Left axis labels column
        axis = ctk.CTkFrame(self.scroll, fg_color="transparent", width=84)
        axis.pack(side="left", fill="y", padx=(2, 6))

        ctk.CTkLabel(
            axis,
            text="Ref Page",
            font=FONTS["small_bold"],
            text_color=COLORS["text_secondary"],
            height=34,
        ).pack(pady=(4, 4))

        for f_idx in range(frame_count):
            ctk.CTkLabel(
                axis,
                text=f"Frame {f_idx + 1}",
                font=FONTS["small_bold"],
                text_color=COLORS["text_muted"],
                height=28 if self._compact else 32,
            ).pack(pady=2)

        ctk.CTkLabel(
            axis,
            text="Outcome",
            font=FONTS["small_bold"],
            text_color=COLORS["text_secondary"],
            height=26,
        ).pack(pady=(4, 2))

        for step in steps:
            page = step.get("page", 0)
            hit = bool(step.get("hit", False))
            replaced = int(step.get("replaced_page", -1))
            frames = step.get("frames", [])

            if hit:
                header_bg = COLORS["success_bg"]
                header_fg = COLORS["success"]
                outcome_text = "HIT"
            elif replaced >= 0:
                header_bg = COLORS["danger_bg"]
                header_fg = COLORS["danger"]
                outcome_text = f"FAULT ({replaced}→{page})" if not self._compact else f"F:{replaced}→{page}"
            else:
                header_bg = COLORS["info_bg"]
                header_fg = COLORS["info"]
                outcome_text = "FAULT"

            col = ctk.CTkFrame(
                self.scroll,
                width=col_w,
                fg_color=COLORS["card_bg"],
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border"],
            )
            col.pack(side="left", padx=3, pady=2)

            # Referenced page badge
            ctk.CTkLabel(
                col,
                text=str(page),
                width=col_w - 8,
                height=30,
                corner_radius=6,
                fg_color=COLORS["primary"],
                text_color="#FFFFFF",
                font=FONTS["body_bold"],
            ).pack(padx=4, pady=(4, 4))

            # Frame slots
            for f_idx in range(frame_count):
                val = frames[f_idx] if f_idx < len(frames) else -1
                if val == -1:
                    slot_bg = COLORS["empty_frame_bg"]
                    slot_fg = COLORS["empty_frame_text"]
                    slot_text = "—"
                elif val == page and hit:
                    slot_bg = COLORS["success_bg"]
                    slot_fg = COLORS["success"]
                    slot_text = str(val)
                elif val == page and not hit and replaced >= 0:
                    slot_bg = COLORS["danger_bg"]
                    slot_fg = COLORS["danger"]
                    slot_text = str(val)
                elif val == page and not hit:
                    slot_bg = COLORS["info_bg"]
                    slot_fg = COLORS["info"]
                    slot_text = str(val)
                else:
                    slot_bg = COLORS["card_alt_bg"]
                    slot_fg = COLORS["text_primary"]
                    slot_text = str(val)

                ctk.CTkLabel(
                    col,
                    text=slot_text,
                    width=col_w - 8,
                    height=26 if self._compact else 30,
                    corner_radius=5,
                    fg_color=slot_bg,
                    text_color=slot_fg,
                    font=FONTS["mono_bold"],
                ).pack(padx=4, pady=2)

            # Bottom hit/fault pill
            ctk.CTkLabel(
                col,
                text=outcome_text,
                width=col_w - 8,
                height=24,
                corner_radius=5,
                fg_color=header_bg,
                text_color=header_fg,
                font=("Segoe UI", 9, "bold"),
            ).pack(padx=4, pady=(4, 4))
