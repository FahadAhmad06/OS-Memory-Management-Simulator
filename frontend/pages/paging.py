"""Paging and Logical-to-Physical Address Translation Simulator page."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import customtkinter as ctk

from backend_bridge import BackendBridge
from components.buttons import DangerButton, NeutralButton, PrimaryButton, SecondaryButton
from components.cards import CardFrame, MetricCard, StatusBanner
from components.paging_visualization import PagingTranslationDiagram
from config import COLORS, FONTS


class PagingPage(ctk.CTkFrame):
    """Independent Paging Simulator backed exclusively by C++ `paging_translate`."""

    def __init__(self, master: Any, bridge: BackendBridge, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge

        # Default educational configuration: 16 KB logical (16 pages of 1024 B), 8 KB physical (8 frames)
        self._page_table_entries: List[Dict[str, Any]] = [
            {"page_number": 0, "present": True, "frame_number": 3},
            {"page_number": 1, "present": True, "frame_number": 6},
            {"page_number": 2, "present": False, "frame_number": -1},
            {"page_number": 3, "present": True, "frame_number": 1},
            {"page_number": 4, "present": True, "frame_number": 5},
        ]
        self._logical_addresses: List[int] = [0, 1050, 2200, 3500, 17000]
        self._last_result: Optional[Dict[str, Any]] = None

        self.banner = StatusBanner(self)
        self._build_ui()
        self._refresh_pt_list_ui()
        self._refresh_addr_list_ui()

    def _build_ui(self) -> None:
        # Top Configuration Grid
        top_grid = ctk.CTkFrame(self, fg_color="transparent")
        top_grid.pack(fill="x", pady=(0, 14))
        top_grid.grid_columnconfigure(0, weight=1, uniform="paging_top")
        top_grid.grid_columnconfigure(1, weight=1, uniform="paging_top")

        # Left Card: Address Space & Page Table Mappings
        space_card = CardFrame(
            top_grid,
            title="1. Memory Geometry & Page Table",
            subtitle="Configure sizes and present page-to-frame mappings",
        )
        space_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        geo_grid = ctk.CTkFrame(space_card, fg_color="transparent")
        geo_grid.pack(fill="x", padx=16, pady=(4, 8))
        geo_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self.logical_size_entry = self._make_labeled_input(geo_grid, 0, "Logical Space (B)", "16384")
        self.physical_size_entry = self._make_labeled_input(geo_grid, 1, "Physical Mem (B)", "8192")
        self.page_size_entry = self._make_labeled_input(geo_grid, 2, "Page Size (B)", "1024")

        # Page Table Entry builder
        pt_add = ctk.CTkFrame(space_card, fg_color=COLORS["card_alt_bg"], corner_radius=10)
        pt_add.pack(fill="x", padx=16, pady=(2, 6))

        self.pt_page_entry = ctk.CTkEntry(
            pt_add,
            placeholder_text="Page #",
            width=75,
            height=32,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["small"],
        )
        self.pt_page_entry.pack(side="left", padx=(8, 4), pady=8)

        self.pt_present_menu = ctk.CTkOptionMenu(
            pt_add,
            values=["Present", "Absent"],
            width=96,
            height=32,
            fg_color=COLORS["primary_soft"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_primary"],
            font=FONTS["small_bold"],
        )
        self.pt_present_menu.set("Present")
        self.pt_present_menu.pack(side="left", padx=4, pady=8)

        self.pt_frame_entry = ctk.CTkEntry(
            pt_add,
            placeholder_text="Frame #",
            width=80,
            height=32,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["small"],
        )
        self.pt_frame_entry.pack(side="left", padx=4, pady=8)

        SecondaryButton(
            pt_add,
            text="+ Map Page",
            width=95,
            height=32,
            command=self._add_or_update_pt_entry,
        ).pack(side="right", padx=(4, 8), pady=8)

        self.pt_list_frame = ctk.CTkScrollableFrame(
            space_card,
            height=130,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=8,
        )
        self.pt_list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Right Card: Logical Addresses Queue
        addr_card = CardFrame(
            top_grid,
            title="2. Logical Addresses to Translate",
            subtitle="Add valid or out-of-bounds logical addresses",
        )
        addr_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        addr_add = ctk.CTkFrame(addr_card, fg_color=COLORS["card_alt_bg"], corner_radius=10)
        addr_add.pack(fill="x", padx=16, pady=(4, 8))

        self.logical_addr_entry = ctk.CTkEntry(
            addr_add,
            placeholder_text="Logical Address (e.g. 2056)",
            width=210,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
        )
        self.logical_addr_entry.pack(side="left", padx=(10, 6), pady=8)

        PrimaryButton(
            addr_add,
            text="+ Add Address",
            width=130,
            height=34,
            command=self._add_logical_address,
        ).pack(side="right", padx=(6, 10), pady=8)

        self.addr_list_frame = ctk.CTkScrollableFrame(
            addr_card,
            height=175,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=8,
        )
        self.addr_list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Action Bar
        action_card = CardFrame(self)
        action_card.pack(fill="x", pady=(0, 14))

        action_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        action_inner.pack(fill="x", padx=16, pady=12)

        self.translate_btn = PrimaryButton(
            action_inner,
            text="▶  Translate Address",
            width=185,
            command=self._run_translation,
        )
        self.translate_btn.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            action_inner,
            text="Click any translated row below to inspect its step-by-step pipeline diagram.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=8)

        NeutralButton(
            action_inner,
            text="Reset",
            width=95,
            command=self._reset,
        ).pack(side="right")

        # KPI Row
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 14))
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="paging_kpi")

        self.kpi_pages = MetricCard(kpi_row, "Total Pages / Frames", "—", COLORS["primary"], "Logical pages vs physical frames")
        self.kpi_pages.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.kpi_used = MetricCard(kpi_row, "Used / Free Frames", "—", COLORS["secondary"], "Distinct mapped frames")
        self.kpi_used.grid(row=0, column=1, sticky="nsew", padx=6)

        self.kpi_util = MetricCard(kpi_row, "Frame Utilization", "0.0%", COLORS["success"], "Physical frame occupancy")
        self.kpi_util.grid(row=0, column=2, sticky="nsew", padx=6)

        self.kpi_valid = MetricCard(kpi_row, "Valid / Faults", "—", COLORS["accent_indigo"], "Translation outcomes")
        self.kpi_valid.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # Visual Translation Pipeline
        self.diagram = PagingTranslationDiagram(self)
        self.diagram.pack(fill="x", pady=(0, 14))

        # Bottom Split: Translation Results Table + Full Page Table
        bottom_grid = ctk.CTkFrame(self, fg_color="transparent")
        bottom_grid.pack(fill="x", pady=(0, 10))
        bottom_grid.grid_columnconfigure(0, weight=3)
        bottom_grid.grid_columnconfigure(1, weight=2)

        tr_card = CardFrame(
            bottom_grid,
            title="Address Translation Results & Step-by-Step Explanation",
            subtitle="Click a row to load into diagram",
        )
        tr_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.translations_frame = ctk.CTkFrame(tr_card, fg_color="transparent")
        self.translations_frame.pack(fill="x", padx=16, pady=(4, 14))
        self._render_empty_translations()

        pt_out_card = CardFrame(
            bottom_grid,
            title="Backend Page Table State",
            subtitle="Present, frame, dirty & referenced bits",
        )
        pt_out_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.pt_output_frame = ctk.CTkScrollableFrame(
            pt_out_card,
            height=240,
            fg_color="transparent",
        )
        self.pt_output_frame.pack(fill="both", expand=True, padx=14, pady=(4, 14))
        self._render_empty_pt_output()

    @staticmethod
    def _make_labeled_input(parent: Any, col: int, label: str, default: str) -> ctk.CTkEntry:
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=col, sticky="ew", padx=4)
        ctk.CTkLabel(
            box,
            text=label,
            font=FONTS["caption"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(fill="x")
        entry = ctk.CTkEntry(
            box,
            height=32,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono_bold"],
        )
        entry.insert(0, default)
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _add_or_update_pt_entry(self) -> None:
        self.banner.hide()
        try:
            page_num = int(self.pt_page_entry.get().strip())
        except ValueError:
            self.banner.show_error("Page number must be a non-negative integer.")
            return

        if page_num < 0:
            self.banner.show_error("Page number cannot be negative.")
            return

        present = self.pt_present_menu.get() == "Present"
        frame_num = -1
        if present:
            try:
                frame_num = int(self.pt_frame_entry.get().strip())
            except ValueError:
                self.banner.show_error("Frame number must be a non-negative integer when page is Present.")
                return
            if frame_num < 0:
                self.banner.show_error("Frame number cannot be negative.")
                return

        updated = False
        for item in self._page_table_entries:
            if item["page_number"] == page_num:
                item["present"] = present
                item["frame_number"] = frame_num if present else -1
                updated = True
                break

        if not updated:
            self._page_table_entries.append(
                {
                    "page_number": page_num,
                    "present": present,
                    "frame_number": frame_num if present else -1,
                }
            )
            self._page_table_entries.sort(key=lambda x: x["page_number"])

        self.pt_page_entry.delete(0, "end")
        self.pt_frame_entry.delete(0, "end")
        self._refresh_pt_list_ui()

    def _remove_pt_entry(self, index: int) -> None:
        if 0 <= index < len(self._page_table_entries):
            self._page_table_entries.pop(index)
            self._refresh_pt_list_ui()

    def _refresh_pt_list_ui(self) -> None:
        for child in self.pt_list_frame.winfo_children():
            child.destroy()

        if not self._page_table_entries:
            ctk.CTkLabel(
                self.pt_list_frame,
                text="No page table mappings configured (all pages default to not present).",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(pady=28)
            return

        for idx, pte in enumerate(self._page_table_entries):
            row = ctk.CTkFrame(self.pt_list_frame, fg_color="#FFFFFF", corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            present = bool(pte["present"])
            frame_txt = f"Frame {pte['frame_number']}" if present else "Not Mapped (-1)"
            badge_bg = COLORS["success_bg"] if present else COLORS["danger_bg"]
            badge_fg = COLORS["success"] if present else COLORS["danger"]

            ctk.CTkLabel(
                row,
                text=f"Page {pte['page_number']}  →  {frame_txt}",
                font=FONTS["mono"],
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=10, pady=5)

            ctk.CTkLabel(
                row,
                text="PRESENT" if present else "ABSENT",
                font=FONTS["caption"],
                fg_color=badge_bg,
                text_color=badge_fg,
                corner_radius=5,
                padx=6,
                pady=2,
            ).pack(side="left", padx=4)

            DangerButton(
                row,
                text="Remove",
                width=72,
                height=26,
                command=lambda i=idx: self._remove_pt_entry(i),
            ).pack(side="right", padx=8, pady=4)

    def _add_logical_address(self) -> None:
        self.banner.hide()
        try:
            addr = int(self.logical_addr_entry.get().strip())
        except ValueError:
            self.banner.show_error("Logical address must be a non-negative integer.")
            return

        if addr < 0:
            self.banner.show_error("Logical address must be >= 0.")
            return

        self._logical_addresses.append(addr)
        self.logical_addr_entry.delete(0, "end")
        self._refresh_addr_list_ui()

    def _remove_logical_address(self, index: int) -> None:
        if 0 <= index < len(self._logical_addresses):
            self._logical_addresses.pop(index)
            self._refresh_addr_list_ui()

    def _refresh_addr_list_ui(self) -> None:
        for child in self.addr_list_frame.winfo_children():
            child.destroy()

        if not self._logical_addresses:
            ctk.CTkLabel(
                self.addr_list_frame,
                text="No logical addresses queued. Add an address above.",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(pady=40)
            return

        for idx, addr in enumerate(self._logical_addresses):
            row = ctk.CTkFrame(self.addr_list_frame, fg_color="#FFFFFF", corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            ctk.CTkLabel(
                row,
                text=f"#{idx + 1}   Logical Address: {addr}  (0x{addr:X})",
                font=FONTS["mono"],
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=10, pady=5)

            DangerButton(
                row,
                text="Remove",
                width=76,
                height=26,
                command=lambda i=idx: self._remove_logical_address(i),
            ).pack(side="right", padx=8, pady=4)

    def _run_translation(self) -> None:
        self.banner.hide()
        try:
            logical_size = int(self.logical_size_entry.get().strip())
            physical_size = int(self.physical_size_entry.get().strip())
            page_size = int(self.page_size_entry.get().strip())
        except ValueError:
            self.banner.show_error("Logical space, physical memory, and page size must be valid integers.")
            return

        if logical_size <= 0 or physical_size <= 0 or page_size <= 0:
            self.banner.show_error("Memory and page sizes must be greater than 0.")
            return

        if not self._logical_addresses:
            self.banner.show_error("Add at least one logical address to translate.")
            return

        payload = {
            "logical_address_space_size": logical_size,
            "physical_memory_size": physical_size,
            "page_size": page_size,
            "page_table": list(self._page_table_entries),
            "logical_addresses": list(self._logical_addresses),
        }

        self.translate_btn.configure(state="disabled")

        def on_ok(result: Dict[str, Any]) -> None:
            self.translate_btn.configure(state="normal")
            self._last_result = result
            self._apply_result(result)
            self.banner.show_success(
                f"Translated {len(result.get('translations', []))} logical address(es) via C++ paging engine."
            )

        def on_err(msg: str) -> None:
            self.translate_btn.configure(state="normal")
            self.banner.show_error(msg)

        self.bridge.execute_async(self, "paging_translate", payload, on_ok, on_err)

    def _apply_result(self, res: Dict[str, Any]) -> None:
        num_pages = int(res.get("num_pages", 0))
        num_frames = int(res.get("num_frames", 0))
        used_frames = int(res.get("used_frames", 0))
        free_frames = int(res.get("free_frames", 0))
        util = float(res.get("frame_utilization", 0.0))
        page_size = int(res.get("page_size", 0))
        translations = res.get("translations", [])

        valid_count = sum(1 for t in translations if t.get("valid"))
        fault_count = len(translations) - valid_count

        self.kpi_pages.set_value(f"{num_pages} P / {num_frames} F", f"Page size: {page_size} B")
        self.kpi_used.set_value(f"{used_frames} / {free_frames}", "Used frames / Free frames")
        self.kpi_util.set_value(f"{util:.2f}%", "Physical frame utilization")
        self.kpi_valid.set_value(f"{valid_count} OK / {fault_count} Err", "Valid vs fault/invalid")

        if translations:
            self.diagram.set_translation(translations[0], page_size=page_size)
        else:
            self.diagram.reset()

        self._render_translations_table(translations, page_size)
        self._render_pt_output(res.get("page_table", []))

    def _render_empty_translations(self) -> None:
        for child in self.translations_frame.winfo_children():
            child.destroy()
        ctk.CTkLabel(
            self.translations_frame,
            text="Click 'Translate Address' to compute page numbers, offsets, and physical addresses.",
            font=FONTS["subtitle"],
            text_color=COLORS["text_muted"],
        ).pack(pady=24)

    def _render_translations_table(self, translations: List[Dict[str, Any]], page_size: int) -> None:
        for child in self.translations_frame.winfo_children():
            child.destroy()

        headers = ["Logical", "Page #", "Offset", "Frame #", "Physical", "Status", "Step Explanation"]
        widths = [72, 62, 62, 70, 82, 85, 250]

        hdr = ctk.CTkFrame(self.translations_frame, fg_color=COLORS["table_header_bg"], corner_radius=8)
        hdr.pack(fill="x", pady=(0, 4))
        for title, w in zip(headers, widths):
            ctk.CTkLabel(
                hdr,
                text=title,
                width=w,
                font=FONTS["small_bold"],
                text_color=COLORS["primary"],
                anchor="w",
            ).pack(side="left", padx=5, pady=7)

        for idx, tr in enumerate(translations):
            valid = bool(tr.get("valid", False))
            row_bg = (COLORS["table_row_even"] if idx % 2 == 0 else COLORS["table_row_odd"]) if valid else COLORS["danger_bg"]
            row = ctk.CTkFrame(
                self.translations_frame,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=COLORS["divider"] if valid else COLORS["danger_border"],
            )
            row.pack(fill="x", pady=2)

            logical_addr = tr.get("logical_address", 0)
            page_num = tr.get("page_number", 0)
            offset = tr.get("offset", 0)
            frame_num = tr.get("frame_number", -1)
            phys_addr = tr.get("physical_address", 0)
            err = str(tr.get("error", "")).strip()

            if valid:
                explanation = f"{logical_addr} ÷ {page_size} = P{page_num} (+{offset}) → F{frame_num}×{page_size}+{offset} = {phys_addr}"
                status_txt = "VALID"
                status_fg = COLORS["success"]
            else:
                explanation = err or "Translation failed"
                status_txt = "INVALID"
                status_fg = COLORS["danger"]

            vals = [
                str(logical_addr),
                str(page_num) if "exceeds" not in err.lower() else "—",
                str(offset) if "exceeds" not in err.lower() else "—",
                str(frame_num) if frame_num >= 0 else "—",
                str(phys_addr) if valid else "—",
                status_txt,
                explanation,
            ]

            for col_i, (val, w) in enumerate(zip(vals, widths)):
                lbl = ctk.CTkLabel(
                    row,
                    text=val,
                    width=w,
                    font=FONTS["small_bold"] if col_i in (0, 4, 5) else FONTS["small"],
                    text_color=status_fg if col_i == 5 else COLORS["text_primary"],
                    anchor="w",
                    wraplength=w if col_i == 6 else 0,
                    justify="left",
                )
                lbl.pack(side="left", padx=5, pady=6)
                lbl.bind("<Button-1>", lambda _e, t=tr, ps=page_size: self.diagram.set_translation(t, ps))

            row.bind("<Button-1>", lambda _e, t=tr, ps=page_size: self.diagram.set_translation(t, ps))

    def _render_empty_pt_output(self) -> None:
        for child in self.pt_output_frame.winfo_children():
            child.destroy()
        ctk.CTkLabel(
            self.pt_output_frame,
            text="Page table state will appear here after translation.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        ).pack(pady=24)

    def _render_pt_output(self, pt_entries: List[Dict[str, Any]]) -> None:
        for child in self.pt_output_frame.winfo_children():
            child.destroy()

        hdr = ctk.CTkFrame(self.pt_output_frame, fg_color=COLORS["table_header_bg"], corner_radius=8)
        hdr.pack(fill="x", pady=(0, 4))
        for title, w in [("Page", 55), ("Present", 72), ("Frame", 62), ("Ref", 48)]:
            ctk.CTkLabel(
                hdr,
                text=title,
                width=w,
                font=FONTS["small_bold"],
                text_color=COLORS["primary"],
                anchor="w",
            ).pack(side="left", padx=6, pady=6)

        for idx, pte in enumerate(pt_entries):
            present = bool(pte.get("present", False))
            bg = COLORS["table_row_even"] if idx % 2 == 0 else COLORS["table_row_odd"]
            row = ctk.CTkFrame(self.pt_output_frame, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=1)

            vals = [
                f"P{pte.get('page_number', idx)}",
                "Yes" if present else "No",
                str(pte.get("frame_number", -1)) if present else "—",
                "1" if pte.get("referenced", False) else "0",
            ]
            for c_i, (val, w) in enumerate(zip(vals, [55, 72, 62, 48])):
                ctk.CTkLabel(
                    row,
                    text=val,
                    width=w,
                    font=FONTS["mono"],
                    text_color=COLORS["success"] if (c_i == 1 and present) else COLORS["text_primary"],
                    anchor="w",
                ).pack(side="left", padx=6, pady=4)

    def _reset(self) -> None:
        self.banner.hide()
        self.logical_size_entry.delete(0, "end")
        self.logical_size_entry.insert(0, "16384")
        self.physical_size_entry.delete(0, "end")
        self.physical_size_entry.insert(0, "8192")
        self.page_size_entry.delete(0, "end")
        self.page_size_entry.insert(0, "1024")

        self._page_table_entries = [
            {"page_number": 0, "present": True, "frame_number": 3},
            {"page_number": 1, "present": True, "frame_number": 6},
            {"page_number": 2, "present": False, "frame_number": -1},
            {"page_number": 3, "present": True, "frame_number": 1},
            {"page_number": 4, "present": True, "frame_number": 5},
        ]
        self._logical_addresses = [0, 1050, 2200, 3500, 17000]
        self._refresh_pt_list_ui()
        self._refresh_addr_list_ui()

        self.kpi_pages.set_value("—", "Logical pages vs physical frames")
        self.kpi_used.set_value("—", "Distinct mapped frames")
        self.kpi_util.set_value("0.0%", "Physical frame utilization")
        self.kpi_valid.set_value("—", "Translation outcomes")

        self.diagram.reset()
        self._render_empty_translations()
        self._render_empty_pt_output()
