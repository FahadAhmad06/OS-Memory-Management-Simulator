"""Dedicated Algorithm Comparison page for Contiguous Allocation and Page Replacement."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from backend_bridge import BackendBridge
from components.buttons import NeutralButton, PrimaryButton
from components.cards import CardFrame, StatusBanner
from components.charts import ComparisonChartWidget
from components.memory_visualization import MemoryBlockCanvas
from components.page_frame_visualization import PageFrameTimeline
from config import COLORS, FONTS


class ComparisonPage(ctk.CTkFrame):
    """
    Side-by-side comparison page with two independent sections:
      A. Memory Allocation Comparison (`compare_allocation`: First Fit vs Best Fit vs Worst Fit)
      B. Page Replacement Comparison (`compare_page_replacement`: FIFO vs LRU vs Optimal)
    """

    def __init__(self, master: Any, bridge: BackendBridge, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge
        self.banner = StatusBanner(self)
        self._build_ui()

    def _build_ui(self) -> None:
        # =====================================================================
        # SECTION A: MEMORY ALLOCATION COMPARISON
        # =====================================================================
        sec_a = CardFrame(
            self,
            title="A. Memory Allocation Comparison (First Fit vs Best Fit vs Worst Fit)",
            subtitle="Evaluates all three contiguous strategies on identical input via compare_allocation",
        )
        sec_a.pack(fill="x", pady=(0, 18))

        # Section A Inputs
        a_in = ctk.CTkFrame(sec_a, fg_color=COLORS["card_alt_bg"], corner_radius=10)
        a_in.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(
            a_in,
            text="Total Memory (KB):",
            font=FONTS["small_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(12, 6), pady=10)

        self.alloc_total_entry = ctk.CTkEntry(
            a_in,
            width=100,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono_bold"],
        )
        self.alloc_total_entry.insert(0, "1024")
        self.alloc_total_entry.pack(side="left", padx=(0, 14), pady=10)

        ctk.CTkLabel(
            a_in,
            text="Processes (PID:Size):",
            font=FONTS["small_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 6), pady=10)

        self.alloc_procs_entry = ctk.CTkEntry(
            a_in,
            width=330,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono"],
        )
        self.alloc_procs_entry.insert(0, "P1:212, P2:417, P3:112, P4:426")
        self.alloc_procs_entry.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)

        self.run_alloc_btn = PrimaryButton(
            a_in,
            text="▶  Run Allocation Comparison",
            width=210,
            height=34,
            command=self._run_allocation_comparison,
        )
        self.run_alloc_btn.pack(side="left", padx=4, pady=10)

        NeutralButton(
            a_in,
            text="Clear Results",
            width=105,
            height=34,
            command=self._clear_allocation_results,
        ).pack(side="right", padx=(4, 12), pady=10)

        # Three Algorithm Cards
        a_cards_grid = ctk.CTkFrame(sec_a, fg_color="transparent")
        a_cards_grid.pack(fill="x", padx=16, pady=(0, 12))
        a_cards_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="comp_alloc_cards")

        self._alloc_card_widgets: Dict[str, Dict[str, Any]] = {}
        for col_i, (title, key) in enumerate(
            [("First Fit", "first_fit"), ("Best Fit", "best_fit"), ("Worst Fit", "worst_fit")]
        ):
            card = ctk.CTkFrame(
                a_cards_grid,
                fg_color=COLORS["card_alt_bg"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border_strong"],
            )
            card.grid(row=0, column=col_i, sticky="nsew", padx=4)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Segoe UI", 15, "bold"),
                text_color=COLORS["primary"],
            ).pack(anchor="w", padx=12, pady=(10, 6))

            mem_vis = MemoryBlockCanvas(card, canvas_height=96)
            mem_vis.pack(fill="x", padx=10, pady=(0, 8))

            stats_lbl = ctk.CTkLabel(
                card,
                text="Run comparison to populate metrics.",
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w",
                justify="left",
                wraplength=310,
            )
            stats_lbl.pack(fill="x", padx=12, pady=(0, 10))

            self._alloc_card_widgets[key] = {
                "canvas": mem_vis,
                "stats": stats_lbl,
            }

        # Section A Chart + Table Row
        a_bottom = ctk.CTkFrame(sec_a, fg_color="transparent")
        a_bottom.pack(fill="x", padx=16, pady=(0, 10))
        a_bottom.grid_columnconfigure(0, weight=2)
        a_bottom.grid_columnconfigure(1, weight=3)

        self.alloc_chart = ComparisonChartWidget(a_bottom, figsize=(4.6, 2.9))
        self.alloc_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.alloc_table_box = ctk.CTkFrame(
            a_bottom,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.alloc_table_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._render_alloc_table(None)

        # Section A Insights & Conclusion
        self.alloc_insights_box = ctk.CTkFrame(
            sec_a,
            fg_color=COLORS["primary_soft"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border_strong"],
        )
        self.alloc_insights_box.pack(fill="x", padx=16, pady=(4, 14))
        self.alloc_insights_lbl = ctk.CTkLabel(
            self.alloc_insights_box,
            text="Key Insights & Final Conclusion will be generated dynamically from backend metrics for your current input.",
            font=FONTS["small"],
            text_color=COLORS["text_primary"],
            anchor="w",
            justify="left",
            wraplength=980,
        )
        self.alloc_insights_lbl.pack(fill="x", padx=14, pady=10)

        # =====================================================================
        # SECTION B: PAGE REPLACEMENT COMPARISON
        # =====================================================================
        sec_b = CardFrame(
            self,
            title="B. Page Replacement Comparison (FIFO vs LRU vs Optimal)",
            subtitle="Evaluates all three page replacement policies on identical input via compare_page_replacement",
        )
        sec_b.pack(fill="x", pady=(0, 12))

        b_in = ctk.CTkFrame(sec_b, fg_color=COLORS["card_alt_bg"], corner_radius=10)
        b_in.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(
            b_in,
            text="Frames:",
            font=FONTS["small_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(12, 6), pady=10)

        self.pr_frames_entry = ctk.CTkEntry(
            b_in,
            width=75,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono_bold"],
        )
        self.pr_frames_entry.insert(0, "3")
        self.pr_frames_entry.pack(side="left", padx=(0, 14), pady=10)

        ctk.CTkLabel(
            b_in,
            text="Reference String:",
            font=FONTS["small_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 6), pady=10)

        self.pr_refs_entry = ctk.CTkEntry(
            b_in,
            width=340,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono"],
        )
        self.pr_refs_entry.insert(0, "7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2")
        self.pr_refs_entry.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)

        self.run_pr_btn = PrimaryButton(
            b_in,
            text="▶  Run Replacement Comparison",
            width=225,
            height=34,
            command=self._run_pr_comparison,
        )
        self.run_pr_btn.pack(side="left", padx=4, pady=10)

        NeutralButton(
            b_in,
            text="Clear Results",
            width=105,
            height=34,
            command=self._clear_pr_results,
        ).pack(side="right", padx=(4, 12), pady=10)

        # Three Algorithm Cards for FIFO, LRU, Optimal
        b_cards_grid = ctk.CTkFrame(sec_b, fg_color="transparent")
        b_cards_grid.pack(fill="x", padx=16, pady=(0, 12))
        b_cards_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="comp_pr_cards")

        self._pr_card_widgets: Dict[str, Dict[str, Any]] = {}
        for col_i, (title, key) in enumerate([("FIFO", "fifo"), ("LRU", "lru"), ("Optimal", "optimal")]):
            card = ctk.CTkFrame(
                b_cards_grid,
                fg_color=COLORS["card_alt_bg"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border_strong"],
            )
            card.grid(row=0, column=col_i, sticky="nsew", padx=4)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Segoe UI", 15, "bold"),
                text_color=COLORS["primary"],
            ).pack(anchor="w", padx=12, pady=(10, 6))

            timeline = PageFrameTimeline(card, compact=True)
            timeline.pack(fill="x", padx=10, pady=(0, 8))

            stats_lbl = ctk.CTkLabel(
                card,
                text="Run comparison to view hits, faults, and ratios.",
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w",
                justify="left",
            )
            stats_lbl.pack(fill="x", padx=12, pady=(0, 10))

            self._pr_card_widgets[key] = {
                "timeline": timeline,
                "stats": stats_lbl,
            }

        # Charts Row: Page Faults Chart + Page Hits Chart
        charts_row = ctk.CTkFrame(sec_b, fg_color="transparent")
        charts_row.pack(fill="x", padx=16, pady=(0, 12))
        charts_row.grid_columnconfigure((0, 1), weight=1, uniform="pr_charts")

        self.faults_chart = ComparisonChartWidget(charts_row, figsize=(5.2, 2.9))
        self.faults_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.hits_chart = ComparisonChartWidget(charts_row, figsize=(5.2, 2.9))
        self.hits_chart.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Section B Comparison Table
        self.pr_table_box = ctk.CTkFrame(
            sec_b,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.pr_table_box.pack(fill="x", padx=16, pady=(0, 10))
        self._render_pr_table(None)

        # Section B Insights & Conclusion
        self.pr_insights_box = ctk.CTkFrame(
            sec_b,
            fg_color=COLORS["primary_soft"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border_strong"],
        )
        self.pr_insights_box.pack(fill="x", padx=16, pady=(0, 14))
        self.pr_insights_lbl = ctk.CTkLabel(
            self.pr_insights_box,
            text="Key Insights & Final Conclusion will evaluate which algorithm achieved the fewest page faults on your specific reference string.",
            font=FONTS["small"],
            text_color=COLORS["text_primary"],
            anchor="w",
            justify="left",
            wraplength=980,
        )
        self.pr_insights_lbl.pack(fill="x", padx=14, pady=10)

    # =========================================================================
    # Section A Handlers
    # =========================================================================
    def _parse_allocation_inputs(self) -> Optional[Dict[str, Any]]:
        try:
            total_memory = int(self.alloc_total_entry.get().strip())
        except ValueError:
            self.banner.show_error("Total Memory in Section A must be a positive integer.")
            return None

        if total_memory <= 0:
            self.banner.show_error("Total Memory must be greater than 0.")
            return None

        raw = self.alloc_procs_entry.get().strip()
        if not raw:
            self.banner.show_error("Enter process pairs in the format PID:Size (e.g., P1:212, P2:417).")
            return None

        requests: List[Dict[str, Any]] = []
        for idx, token in enumerate([t.strip() for t in raw.split(",") if t.strip()], start=1):
            if ":" in token:
                pid_part, size_part = token.split(":", 1)
                pid = pid_part.strip() or f"P{idx}"
                raw_sz = size_part.strip()
            else:
                pid = f"P{idx}"
                raw_sz = token

            try:
                sz = int(raw_sz)
            except ValueError:
                self.banner.show_error(f"Invalid size in '{token}'. Use PID:Size format (e.g., P1:200).")
                return None

            if sz <= 0:
                self.banner.show_error(f"Process '{pid}' size must be greater than 0.")
                return None

            requests.append({"process_id": pid, "size": sz})

        return {
            "total_memory": total_memory,
            "initial_blocks": [],
            "requests": requests,
        }

    def _run_allocation_comparison(self) -> None:
        self.banner.hide()
        payload = self._parse_allocation_inputs()
        if payload is None:
            return

        self.run_alloc_btn.configure(state="disabled")

        def on_ok(comp: Dict[str, Any]) -> None:
            self.run_alloc_btn.configure(state="normal")
            self._apply_allocation_comparison(comp)
            self.banner.show_success("Memory Allocation comparison completed across First Fit, Best Fit, and Worst Fit.")

        def on_err(msg: str) -> None:
            self.run_alloc_btn.configure(state="normal")
            self.banner.show_error(msg)

        self.bridge.execute_async(self, "compare_allocation", payload, on_ok, on_err)

    def _apply_allocation_comparison(self, comp: Dict[str, Any]) -> None:
        for key in ("first_fit", "best_fit", "worst_fit"):
            data = comp.get(key, {})
            widgets = self._alloc_card_widgets[key]
            widgets["canvas"].set_data(int(data.get("total_memory", 0)), data.get("memory_blocks", []))

            order_items = [
                f"{r.get('process_id')}({'OK' if r.get('allocated') else 'FAIL'})"
                for r in data.get("results", [])
            ]
            order_str = " → ".join(order_items) if order_items else "None"

            summary_text = (
    f"Allocation Order: {order_str}\n"
    f"Successful: {data.get('successful_allocations', 0)}   |   "
    f"Failed: {data.get('failed_allocations', 0)}\n"
    f"Memory Used: {data.get('allocated_memory', 0)} / "
    f"{data.get('total_memory', 0)} KB   |   "
    f"Utilization: {float(data.get('memory_utilization', 0.0)):.2f}%\n"
    f"Internal Fragmentation: "
    f"{data.get('total_internal_fragmentation', 0)} KB"
)
            widgets["stats"].configure(text=summary_text)

        self.alloc_chart.plot_grouped_allocation_metrics(comp)
        self._render_alloc_table(comp)
        self._update_alloc_insights(comp)

    def _render_alloc_table(self, comp: Optional[Dict[str, Any]]) -> None:
        for child in self.alloc_table_box.winfo_children():
            child.destroy()

        headers = ["Metric", "First Fit", "Best Fit", "Worst Fit"]
        widths = [185, 110, 110, 110]

        hdr = ctk.CTkFrame(self.alloc_table_box, fg_color=COLORS["table_header_bg"], corner_radius=8)
        hdr.pack(fill="x", padx=10, pady=(10, 4))
        for t, w in zip(headers, widths):
            ctk.CTkLabel(
                hdr,
                text=t,
                width=w,
                font=FONTS["small_bold"],
                text_color=COLORS["primary"],
                anchor="w",
            ).pack(side="left", padx=6, pady=6)

        if not comp:
            ctk.CTkLabel(
                self.alloc_table_box,
                text="Run Allocation Comparison to populate metrics table.",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(pady=40)
            return

        rows = [
            ("Successful Allocations", lambda d: str(d.get("successful_allocations", 0))),
            ("Failed Allocations", lambda d: str(d.get("failed_allocations", 0))),
            ("Allocated Memory", lambda d: f"{d.get('allocated_memory', 0)} KB"),
            ("Remaining Free Memory", lambda d: f"{d.get('free_memory', 0)} KB"),
            ("Memory Utilization", lambda d: f"{float(d.get('memory_utilization', 0.0)):.2f}%"),
            ("Internal Fragmentation", lambda d: f"{d.get('total_internal_fragmentation', 0)} KB"),
        ]

        for idx, (label, fn) in enumerate(rows):
            bg = COLORS["table_row_even"] if idx % 2 == 0 else COLORS["table_row_odd"]
            r = ctk.CTkFrame(self.alloc_table_box, fg_color=bg, corner_radius=6)
            r.pack(fill="x", padx=10, pady=2)

            vals = [
                label,
                fn(comp.get("first_fit", {})),
                fn(comp.get("best_fit", {})),
                fn(comp.get("worst_fit", {})),
            ]
            for c_i, (val, w) in enumerate(zip(vals, widths)):
                ctk.CTkLabel(
                    r,
                    text=val,
                    width=w,
                    font=FONTS["small_bold"] if c_i == 0 else FONTS["mono"],
                    text_color=COLORS["text_primary"],
                    anchor="w",
                ).pack(side="left", padx=6, pady=5)

    def _update_alloc_insights(self, comp: Dict[str, Any]) -> None:
        labels = {"first_fit": "First Fit", "best_fit": "Best Fit", "worst_fit": "Worst Fit"}
        scores = {
            k: (
                int(comp.get(k, {}).get("successful_allocations", 0)),
                float(comp.get(k, {}).get("memory_utilization", 0.0)),
            )
            for k in labels
        }
        best_score = max(scores.values())
        winners = [labels[k] for k, sc in scores.items() if sc == best_score]

        if len(winners) == 3:
            conclusion = (
                "Final Conclusion (Current Input): All three algorithms achieved identical allocation counts "
                f"({best_score[0]} allocated) and memory utilization ({best_score[1]:.2f}%) on this workload."
            )
        else:
            winner_str = " and ".join(winners)
            conclusion = (
                f"Final Conclusion (Current Input): {winner_str} performed best for this specific request sequence "
                f"with {best_score[0]} successful allocation(s) and {best_score[1]:.2f}% memory utilization."
            )

        insights = (
            "Key Insights: Contiguous allocation performance depends directly on partition sizes and arrival order. "
            "First Fit stops at the earliest sufficient free block, Best Fit leaves the smallest residual hole, "
            "and Worst Fit splits the largest free region."
            f"{conclusion}"
        )
        self.alloc_insights_lbl.configure(text=insights)

    def _clear_allocation_results(self) -> None:
        for key in ("first_fit", "best_fit", "worst_fit"):
            self._alloc_card_widgets[key]["canvas"].clear()
            self._alloc_card_widgets[key]["stats"].configure(text="Run comparison to populate metrics.")
        self.alloc_chart.draw_empty("Run allocation comparison to view chart")
        self._render_alloc_table(None)
        self.alloc_insights_lbl.configure(
            text="Key Insights & Final Conclusion will be generated dynamically from backend metrics for your current input."
        )

    # =========================================================================
    # Section B Handlers
    # =========================================================================
    def _parse_pr_inputs(self) -> Optional[Dict[str, Any]]:
        try:
            frame_count = int(self.pr_frames_entry.get().strip())
        except ValueError:
            self.banner.show_error("Frames in Section B must be a positive integer.")
            return None

        if frame_count <= 0 or frame_count > 32:
            self.banner.show_error("Frames must be between 1 and 32.")
            return None

        raw_refs = self.pr_refs_entry.get().strip()
        tokens = [t for t in re.split(r"[\s,;]+", raw_refs) if t]
        refs: List[int] = []
        for tok in tokens:
            try:
                val = int(tok)
            except ValueError:
                self.banner.show_error(f"Invalid page '{tok}' in reference string.")
                return None
            if val < 0:
                self.banner.show_error("Page numbers must be non-negative.")
                return None
            refs.append(val)

        if not refs:
            self.banner.show_error("Enter at least one page number in Section B reference string.")
            return None

        return {"frame_count": frame_count, "reference_string": refs}

    def _run_pr_comparison(self) -> None:
        self.banner.hide()
        payload = self._parse_pr_inputs()
        if payload is None:
            return

        self.run_pr_btn.configure(state="disabled")

        def on_ok(comp: Dict[str, Any]) -> None:
            self.run_pr_btn.configure(state="normal")
            self._apply_pr_comparison(comp)
            self.banner.show_success("Page Replacement comparison completed across FIFO, LRU, and Optimal.")

        def on_err(msg: str) -> None:
            self.run_pr_btn.configure(state="normal")
            self.banner.show_error(msg)

        self.bridge.execute_async(self, "compare_page_replacement", payload, on_ok, on_err)

    def _apply_pr_comparison(self, comp: Dict[str, Any]) -> None:
        for key in ("fifo", "lru", "optimal"):
            data = comp.get(key, {})
            widgets = self._pr_card_widgets[key]
            widgets["timeline"].set_steps(int(data.get("frame_count", 0)), data.get("steps", []))

            faults = int(data.get("faults", 0))
            hits = int(data.get("hits", 0))
            hit_ratio = float(data.get("hit_ratio", 0.0)) * 100.0
            fault_ratio = float(data.get("fault_ratio", 0.0)) * 100.0

            widgets["stats"].configure(
                text=(
                    f"Total Page Faults: {faults}   |   Total Page Hits: {hits}"
                    f"Hit Ratio: {hit_ratio:.2f}%   |   Fault Ratio: {fault_ratio:.2f}%"
                )
            )

        categories = ["FIFO", "LRU", "Optimal"]
        fault_vals = [int(comp.get(k, {}).get("faults", 0)) for k in ("fifo", "lru", "optimal")]
        hit_vals = [int(comp.get(k, {}).get("hits", 0)) for k in ("fifo", "lru", "optimal")]

        self.faults_chart.plot_bar_comparison(
            title="Total Page Faults (Lower is Better)",
            categories=categories,
            values=fault_vals,
            ylabel="Page Faults",
            bar_colors=["#DC2626", "#2563EB", "#0D9488"],
        )
        self.hits_chart.plot_bar_comparison(
            title="Total Page Hits (Higher is Better)",
            categories=categories,
            values=hit_vals,
            ylabel="Page Hits",
            bar_colors=["#0284C7", "#1D4ED8", "#16A34A"],
        )

        self._render_pr_table(comp)
        self._update_pr_insights(comp)

    def _render_pr_table(self, comp: Optional[Dict[str, Any]]) -> None:
        for child in self.pr_table_box.winfo_children():
            child.destroy()

        headers = ["Metric", "FIFO", "LRU", "Optimal"]
        widths = [240, 180, 180, 180]

        hdr = ctk.CTkFrame(self.pr_table_box, fg_color=COLORS["table_header_bg"], corner_radius=8)
        hdr.pack(fill="x", padx=12, pady=(10, 4))
        for t, w in zip(headers, widths):
            ctk.CTkLabel(
                hdr,
                text=t,
                width=w,
                font=FONTS["small_bold"],
                text_color=COLORS["primary"],
                anchor="w",
            ).pack(side="left", padx=8, pady=6)

        if not comp:
            ctk.CTkLabel(
                self.pr_table_box,
                text="Run Page Replacement Comparison to view side-by-side table.",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(pady=24)
            return

        rows = [
            ("Total Page Faults", lambda d: str(d.get("faults", 0))),
            ("Total Page Hits", lambda d: str(d.get("hits", 0))),
            ("Hit Ratio (%)", lambda d: f"{float(d.get('hit_ratio', 0.0)) * 100.0:.2f}%"),
            ("Fault Ratio (%)", lambda d: f"{float(d.get('fault_ratio', 0.0)) * 100.0:.2f}%"),
        ]

        for idx, (label, fn) in enumerate(rows):
            bg = COLORS["table_row_even"] if idx % 2 == 0 else COLORS["table_row_odd"]
            r = ctk.CTkFrame(self.pr_table_box, fg_color=bg, corner_radius=6)
            r.pack(fill="x", padx=12, pady=2)

            vals = [
                label,
                fn(comp.get("fifo", {})),
                fn(comp.get("lru", {})),
                fn(comp.get("optimal", {})),
            ]
            for c_i, (val, w) in enumerate(zip(vals, widths)):
                ctk.CTkLabel(
                    r,
                    text=val,
                    width=w,
                    font=FONTS["small_bold"] if c_i == 0 else FONTS["mono"],
                    text_color=COLORS["text_primary"],
                    anchor="w",
                ).pack(side="left", padx=8, pady=5)

        ctk.CTkFrame(self.pr_table_box, height=8, fg_color="transparent").pack()

    def _update_pr_insights(self, comp: Dict[str, Any]) -> None:
        labels = {"fifo": "FIFO", "lru": "LRU", "optimal": "Optimal"}
        faults = {k: int(comp.get(k, {}).get("faults", 0)) for k in labels}
        hits = {k: int(comp.get(k, {}).get("hits", 0)) for k in labels}
        min_faults = min(faults.values())
        winners = [labels[k] for k, f in faults.items() if f == min_faults]

        winner_str = " and ".join(winners)
        conclusion = (
            f"Final Conclusion (Current Input): {winner_str} achieved the lowest page fault count "
            f"({min_faults} fault(s), {hits[winners[0].lower()] if len(winners) == 1 else max(hits.values())} hit(s)) "
            "for this specific reference string and frame capacity."
        )
        insights = (
            "Key Insights: FIFO evicts the oldest resident page regardless of access frequency; "
            "LRU exploits temporal locality by replacing the least recently referenced page; "
            "Optimal serves as the theoretical benchmark for the given reference sequence."
            f"{conclusion}"
        )
        self.pr_insights_lbl.configure(text=insights)

    def _clear_pr_results(self) -> None:
        for key in ("fifo", "lru", "optimal"):
            self._pr_card_widgets[key]["timeline"].clear()
            self._pr_card_widgets[key]["stats"].configure(text="Run comparison to view hits, faults, and ratios.")
        self.faults_chart.draw_empty("Run comparison to view page faults chart")
        self.hits_chart.draw_empty("Run comparison to view page hits chart")
        self._render_pr_table(None)
        self.pr_insights_lbl.configure(
            text="Key Insights & Final Conclusion will evaluate which algorithm achieved the fewest page faults on your specific reference string."
        )
