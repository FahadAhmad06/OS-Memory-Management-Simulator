"""Visual logical-to-physical address translation diagram component."""

from __future__ import annotations

from typing import Any, Dict, Optional
import customtkinter as ctk

from config import COLORS, FONTS


class PagingTranslationDiagram(ctk.CTkFrame):
    """Displays Logical Address -> [Page # | Offset] -> Page Table -> [Frame # | Offset] -> Physical Address."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(
            master,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._build_ui()

    def _build_ui(self) -> None:
        top_lbl = ctk.CTkLabel(
            self,
            text="ADDRESS TRANSLATION PIPELINE",
            font=FONTS["small_bold"],
            text_color=COLORS["primary"],
            anchor="w",
        )
        top_lbl.pack(fill="x", padx=16, pady=(12, 8))

        flow = ctk.CTkFrame(self, fg_color="transparent")
        flow.pack(fill="x", padx=14, pady=(0, 14))

        # 1. Logical Address Box
        self.logical_box = self._make_stage(flow, "1. Logical Address", "—", COLORS["primary"])
        self.logical_box.pack(side="left", fill="both", expand=True, padx=4)

        self._make_arrow(flow).pack(side="left", padx=2)

        # 2. Decomposition [Page # | Offset]
        self.split_box = self._make_stage(flow, "2. Page #  |  Offset", "P: —  |  d: —", COLORS["secondary"])
        self.split_box.pack(side="left", fill="both", expand=True, padx=4)

        self._make_arrow(flow).pack(side="left", padx=2)

        # 3. Page Table Lookup
        self.pt_box = self._make_stage(flow, "3. Page Table Lookup", "Status: —", COLORS["accent_indigo"])
        self.pt_box.pack(side="left", fill="both", expand=True, padx=4)

        self._make_arrow(flow).pack(side="left", padx=2)

        # 4. Physical Frame + Offset
        self.frame_box = self._make_stage(flow, "4. Frame #  |  Offset", "F: —  |  d: —", COLORS["secondary"])
        self.frame_box.pack(side="left", fill="both", expand=True, padx=4)

        self._make_arrow(flow).pack(side="left", padx=2)

        # 5. Final Physical Address
        self.phys_box = self._make_stage(flow, "5. Physical Address", "—", COLORS["success"])
        self.phys_box.pack(side="left", fill="both", expand=True, padx=4)

    def _make_stage(self, parent: Any, title: str, initial: str, accent: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border_strong"],
        )
        bar = ctk.CTkFrame(card, height=4, fg_color=accent, corner_radius=2)
        bar.pack(fill="x", padx=10, pady=(8, 6))

        t_lbl = ctk.CTkLabel(
            card,
            text=title,
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        t_lbl.pack(padx=10)

        val_lbl = ctk.CTkLabel(
            card,
            text=initial,
            font=FONTS["mono_bold"],
            text_color=COLORS["text_primary"],
            wraplength=175,
        )
        val_lbl.pack(padx=10, pady=(4, 10))
        card.value_label = val_lbl  # type: ignore[attr-defined]
        card.accent_bar = bar  # type: ignore[attr-defined]
        return card

    @staticmethod
    def _make_arrow(parent: Any) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent,
            text="➜",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["primary"],
        )

    def set_translation(self, tr: Optional[Dict[str, Any]], page_size: int = 0) -> None:
        if not tr:
            self.reset()
            return

        logical_addr = tr.get("logical_address", 0)
        page_num = tr.get("page_number", 0)
        offset = tr.get("offset", 0)
        present = bool(tr.get("present", False))
        valid = bool(tr.get("valid", False))
        frame_num = tr.get("frame_number", -1)
        phys_addr = tr.get("physical_address", 0)
        err = str(tr.get("error", "")).strip()

        self.logical_box.value_label.configure(text=f"{logical_addr}")
        if err and "exceeds" in err.lower():
            self.split_box.value_label.configure(text="Out of Bounds")
            self.pt_box.value_label.configure(text="Invalid Address", text_color=COLORS["danger"])
            self.pt_box.accent_bar.configure(fg_color=COLORS["danger"])
            self.frame_box.value_label.configure(text="N/A")
            self.phys_box.value_label.configure(text="FAULT / INVALID", text_color=COLORS["danger"])
            self.phys_box.accent_bar.configure(fg_color=COLORS["danger"])
            return

        self.split_box.value_label.configure(text=f"Page {page_num}  |  +{offset}")

        if valid and present and frame_num >= 0:
            self.pt_box.value_label.configure(
                text=f"Present → Frame {frame_num}",
                text_color=COLORS["success"],
            )
            self.pt_box.accent_bar.configure(fg_color=COLORS["success"])
            self.frame_box.value_label.configure(text=f"Frame {frame_num}  |  +{offset}")
            calc_hint = f"{phys_addr}" if page_size <= 0 else f"{phys_addr} ({frame_num}×{page_size}+{offset})"
            self.phys_box.value_label.configure(text=calc_hint, text_color=COLORS["success"])
            self.phys_box.accent_bar.configure(fg_color=COLORS["success"])
        else:
            self.pt_box.value_label.configure(
                text="Not Present (Page Fault)",
                text_color=COLORS["danger"],
            )
            self.pt_box.accent_bar.configure(fg_color=COLORS["danger"])
            self.frame_box.value_label.configure(text="No Frame Mapped")
            self.phys_box.value_label.configure(
                text="PAGE FAULT",
                text_color=COLORS["danger"],
            )
            self.phys_box.accent_bar.configure(fg_color=COLORS["danger"])

    def reset(self) -> None:
        self.logical_box.value_label.configure(text="—")
        self.split_box.value_label.configure(text="P: —  |  d: —")
        self.pt_box.value_label.configure(text="Status: —", text_color=COLORS["text_primary"])
        self.pt_box.accent_bar.configure(fg_color=COLORS["accent_indigo"])
        self.frame_box.value_label.configure(text="F: —  |  d: —")
        self.phys_box.value_label.configure(text="—", text_color=COLORS["text_primary"])
        self.phys_box.accent_bar.configure(fg_color=COLORS["success"])
