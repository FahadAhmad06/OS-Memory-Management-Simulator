"""Page Replacement Simulator page (FIFO, LRU, Optimal) with dynamic frame columns and timeline."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from backend_bridge import BackendBridge
from components.buttons import NeutralButton, PrimaryButton, SecondaryButton
from components.cards import CardFrame, MetricCard, StatusBanner
from components.page_frame_visualization import PageFrameTimeline
from config import COLORS, FONTS


class PageReplacementPage(ctk.CTkFrame):
    """Virtual memory page replacement module backed by C++ `fifo`, `lru`, `optimal`, and `compare_page_replacement`."""

    ALGO_MAP = {
        "FIFO": "fifo",
        "LRU": "lru",
        "Optimal": "optimal",
    }

    DEFAULT_REF_STRING = "7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2"

    def __init__(self, master: Any, bridge: BackendBridge, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge
        self.banner = StatusBanner(self)
        self._build_ui()

    def _build_ui(self) -> None:
        # Configuration & Controls Card
        cfg_card = CardFrame(
            self,
            title="Page Replacement Simulation Parameters",
            subtitle="FIFO • Least Recently Used (LRU) • Optimal",
        )
        cfg_card.pack(fill="x", pady=(0, 14))

        inputs_row = ctk.CTkFrame(cfg_card, fg_color="transparent")
        inputs_row.pack(fill="x", padx=16, pady=(4, 10))

        # Number of Frames
        f_box = ctk.CTkFrame(inputs_row, fg_color="transparent")
        f_box.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(
            f_box,
            text="Number of Frames:",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")
        self.frame_count_entry = ctk.CTkEntry(
            f_box,
            width=130,
            height=36,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono_bold"],
        )
        self.frame_count_entry.insert(0, "3")
        self.frame_count_entry.pack(anchor="w", pady=(4, 0))

        # Reference String
        r_box = ctk.CTkFrame(inputs_row, fg_color="transparent")
        r_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            r_box,
            text="Page Reference String (comma or space separated integers):",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")
        self.ref_string_entry = ctk.CTkEntry(
            r_box,
            height=36,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono"],
        )
        self.ref_string_entry.insert(0, self.DEFAULT_REF_STRING)
        self.ref_string_entry.pack(fill="x", pady=(4, 0))

        # Algorithm Selector & Action Buttons
        btn_row = ctk.CTkFrame(cfg_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(4, 14))

        ctk.CTkLabel(
            btn_row,
            text="Select Algorithm:",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 8))

        self.algo_selector = ctk.CTkSegmentedButton(
            btn_row,
            values=["FIFO", "LRU", "Optimal"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["primary_soft"],
            unselected_hover_color=COLORS["primary_light"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_bold"],
            height=36,
        )
        self.algo_selector.set("FIFO")
        self.algo_selector.pack(side="left", padx=(0, 14))

        self.run_btn = PrimaryButton(
            btn_row,
            text="▶  Run Simulation",
            width=165,
            command=self._run_single,
        )
        self.run_btn.pack(side="left", padx=4)

        self.run_all_btn = SecondaryButton(
            btn_row,
            text="⚡ Run All Algorithms",
            width=180,
            command=self._run_all,
        )
        self.run_all_btn.pack(side="left", padx=4)

        NeutralButton(
            btn_row,
            text="Reset",
            width=95,
            command=self._reset,
        ).pack(side="right")

        # 4 Statistics Cards
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 14))
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="pr_kpi")

        self.kpi_faults = MetricCard(kpi_row, "Total Page Faults", "0", COLORS["danger"], "Misses requiring frame load")
        self.kpi_faults.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.kpi_hits = MetricCard(kpi_row, "Total Page Hits", "0", COLORS["success"], "Served directly from frames")
        self.kpi_hits.grid(row=0, column=1, sticky="nsew", padx=6)

        self.kpi_hit_ratio = MetricCard(kpi_row, "Hit Ratio", "0.00%", COLORS["primary"], "Hits / Total References")
        self.kpi_hit_ratio.grid(row=0, column=2, sticky="nsew", padx=6)

        self.kpi_fault_ratio = MetricCard(kpi_row, "Fault Ratio", "0.00%", COLORS["warning"], "Faults / Total References")
        self.kpi_fault_ratio.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # Horizontal Frame Timeline Visualization
        self.timeline = PageFrameTimeline(self, compact=False)
        self.timeline.pack(fill="x", pady=(0, 14))

        # Optional All-Algorithms Quick Summary Card
        self.all_card = CardFrame(
            self,
            title="All Page Replacement Algorithms Summary (Identical Input)",
            subtitle="FIFO vs LRU vs Optimal",
        )
        self.all_container = ctk.CTkFrame(self.all_card, fg_color="transparent")
        self.all_container.pack(fill="x", padx=16, pady=(4, 14))
        self._all_visible = False

        # Step-by-Step Dynamic Table & Execution Logs
        table_card = CardFrame(
            self,
            title="Step-by-Step Frame Execution Table & Logs",
            subtitle="Frame columns adapt dynamically to Number of Frames",
        )
        table_card.pack(fill="x", pady=(0, 10))

        self.step_table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.step_table_frame.pack(fill="x", padx=16, pady=(4, 14))
        self._render_empty_table()

    def _parse_inputs(self) -> Optional[Dict[str, Any]]:
        try:
            frame_count = int(self.frame_count_entry.get().strip())
        except ValueError:
            self.banner.show_error("Number of Frames must be a positive integer.")
            return None

        if frame_count <= 0 or frame_count > 32:
            self.banner.show_error("Number of Frames must be between 1 and 32.")
            return None

        raw_refs = self.ref_string_entry.get().strip()
        if not raw_refs:
            self.banner.show_error("Please enter a reference string (e.g., 7, 0, 1, 2, 0, 3, 0, 4).")
            return None

        tokens = [t for t in re.split(r"[\s,;]+", raw_refs) if t]
        ref_list: List[int] = []
        for tok in tokens:
            try:
                val = int(tok)
            except ValueError:
                self.banner.show_error(f"Invalid page number '{tok}' in reference string.")
                return None
            if val < 0:
                self.banner.show_error("Page numbers in reference string must be non-negative integers.")
                return None
            ref_list.append(val)

        if not ref_list:
            self.banner.show_error("Reference string must contain at least one page number.")
            return None

        return {
            "frame_count": frame_count,
            "reference_string": ref_list,
        }

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.run_btn.configure(state=state)
        self.run_all_btn.configure(state=state)

    def _run_single(self) -> None:
        self.banner.hide()
        payload = self._parse_inputs()
        if payload is None:
            return

        label = self.algo_selector.get()
        op = self.ALGO_MAP.get(label, "fifo")
        self._set_busy(True)

        def on_ok(result: Dict[str, Any]) -> None:
            self._set_busy(False)
            self._hide_all_card()
            self._apply_result(result)
            self.banner.show_success(
                f"{label} simulation finished: {result.get('faults', 0)} faults, {result.get('hits', 0)} hits."
            )

        def on_err(msg: str) -> None:
            self._set_busy(False)
            self.banner.show_error(msg)

        self.bridge.execute_async(self, op, payload, on_ok, on_err)

    def _run_all(self) -> None:
        self.banner.hide()
        payload = self._parse_inputs()
        if payload is None:
            return

        self._set_busy(True)

        def on_ok(result: Dict[str, Any]) -> None:
            self._set_busy(False)
            selected_key = self.ALGO_MAP.get(self.algo_selector.get(), "fifo")
            if selected_key in result:
                self._apply_result(result[selected_key])
            self._render_all_summary(result)
            self.banner.show_success("Executed FIFO, LRU, and Optimal on identical reference string.")

        def on_err(msg: str) -> None:
            self._set_busy(False)
            self.banner.show_error(msg)

        self.bridge.execute_async(self, "compare_page_replacement", payload, on_ok, on_err)

    def _apply_result(self, res: Dict[str, Any]) -> None:
        frame_count = int(res.get("frame_count", 0))
        faults = int(res.get("faults", 0))
        hits = int(res.get("hits", 0))
        hit_ratio = float(res.get("hit_ratio", 0.0)) * 100.0
        fault_ratio = float(res.get("fault_ratio", 0.0)) * 100.0
        steps = res.get("steps", [])

        self.kpi_faults.set_value(str(faults), f"Out of {len(steps)} references")
        self.kpi_hits.set_value(str(hits), f"Out of {len(steps)} references")
        self.kpi_hit_ratio.set_value(f"{hit_ratio:.2f}%", f"Ratio: {res.get('hit_ratio', 0.0):.4f}")
        self.kpi_fault_ratio.set_value(f"{fault_ratio:.2f}%", f"Ratio: {res.get('fault_ratio', 0.0):.4f}")

        self.timeline.set_steps(frame_count, steps)
        self._render_step_table(frame_count, steps)

    def _render_all_summary(self, comp: Dict[str, Any]) -> None:
        for child in self.all_container.winfo_children():
            child.destroy()

        grid = ctk.CTkFrame(self.all_container, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="all_pr")

        for col_idx, (title, key) in enumerate([("FIFO", "fifo"), ("LRU", "lru"), ("Optimal", "optimal")]):
            data = comp.get(key, {})
            box = ctk.CTkFrame(
                grid,
                fg_color=COLORS["card_alt_bg"],
                corner_radius=10,
                border_width=1,
                border_color=COLORS["border_strong"],
            )
            box.grid(row=0, column=col_idx, sticky="nsew", padx=4)

            ctk.CTkLabel(
                box,
                text=title,
                font=FONTS["card_title"],
                text_color=COLORS["primary"],
            ).pack(anchor="w", padx=12, pady=(10, 4))

            for line in [
                f"Page Faults: {data.get('faults', 0)}",
                f"Page Hits: {data.get('hits', 0)}",
                f"Hit Ratio: {float(data.get('hit_ratio', 0.0)) * 100.0:.2f}%",
                f"Fault Ratio: {float(data.get('fault_ratio', 0.0)) * 100.0:.2f}%",
            ]:
                ctk.CTkLabel(
                    box,
                    text=line,
                    font=FONTS["small"],
                    text_color=COLORS["text_primary"],
                    anchor="w",
                ).pack(fill="x", padx=12, pady=1)

            ctk.CTkFrame(box, height=8, fg_color="transparent").pack()

        if not self._all_visible:
            self.all_card.pack(fill="x", pady=(0, 14))
            self._all_visible = True

    def _hide_all_card(self) -> None:
        if self._all_visible:
            self.all_card.pack_forget()
            self._all_visible = False

    def _render_empty_table(self) -> None:
        for child in self.step_table_frame.winfo_children():
            child.destroy()
        ctk.CTkLabel(
            self.step_table_frame,
            text="Run FIFO, LRU, or Optimal to populate the step-by-step frame table.",
            font=FONTS["subtitle"],
            text_color=COLORS["text_muted"],
        ).pack(pady=20)

    def _render_step_table(self, frame_count: int, steps: List[Dict[str, Any]]) -> None:
        for child in self.step_table_frame.winfo_children():
            child.destroy()

        headers = ["Step", "Page"] + [f"Frame {i + 1}" for i in range(frame_count)] + ["Hit / Fault", "Replaced Page", "Step Log"]
        frame_w = max(58, min(85, 420 // max(frame_count, 1)))
        widths = [55, 60] + [frame_w] * frame_count + [95, 110, 260]

        hdr = ctk.CTkFrame(self.step_table_frame, fg_color=COLORS["table_header_bg"], corner_radius=8)
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

        for idx, st in enumerate(steps):
            hit = bool(st.get("hit", False))
            replaced = int(st.get("replaced_page", -1))
            page = st.get("page", 0)
            frames = st.get("frames", [])

            row_bg = COLORS["table_row_even"] if idx % 2 == 0 else COLORS["table_row_odd"]
            row = ctk.CTkFrame(
                self.step_table_frame,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=COLORS["divider"],
            )
            row.pack(fill="x", pady=2)

            if hit:
                outcome = "HIT"
                outcome_fg = COLORS["success"]
                rep_txt = "—"
                log_txt = f"Page {page} already resident in frames."
            elif replaced >= 0:
                outcome = "FAULT"
                outcome_fg = COLORS["danger"]
                rep_txt = f"Page {replaced}"
                log_txt = f"Page fault: evicted Page {replaced}, loaded Page {page}."
            else:
                outcome = "FAULT"
                outcome_fg = COLORS["info"]
                rep_txt = "None (Empty Slot)"
                log_txt = f"Page fault: loaded Page {page} into free frame."

            frame_cells = [
                str(frames[f]) if f < len(frames) and frames[f] != -1 else "—"
                for f in range(frame_count)
            ]
            vals = [str(st.get("step", idx + 1)), str(page)] + frame_cells + [outcome, rep_txt, log_txt]

            outcome_col = 2 + frame_count
            for col_i, (val, w) in enumerate(zip(vals, widths)):
                ctk.CTkLabel(
                    row,
                    text=val,
                    width=w,
                    font=FONTS["small_bold"] if col_i in (0, 1, outcome_col) else FONTS["small"],
                    text_color=outcome_fg if col_i == outcome_col else COLORS["text_primary"],
                    anchor="w",
                ).pack(side="left", padx=5, pady=5)

    def _reset(self) -> None:
        self.banner.hide()
        self.frame_count_entry.delete(0, "end")
        self.frame_count_entry.insert(0, "3")
        self.ref_string_entry.delete(0, "end")
        self.ref_string_entry.insert(0, self.DEFAULT_REF_STRING)

        self.kpi_faults.set_value("0", "Misses requiring frame load")
        self.kpi_hits.set_value("0", "Served directly from frames")
        self.kpi_hit_ratio.set_value("0.00%", "Hits / Total References")
        self.kpi_fault_ratio.set_value("0.00%", "Faults / Total References")

        self.timeline.clear()
        self._hide_all_card()
        self._render_empty_table()
