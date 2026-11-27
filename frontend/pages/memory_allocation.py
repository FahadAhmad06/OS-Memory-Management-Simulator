"""Contiguous Memory Allocation Simulator page (First Fit, Best Fit, Worst Fit)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import customtkinter as ctk

from backend_bridge import BackendBridge
from components.buttons import DangerButton, NeutralButton, PrimaryButton, SecondaryButton
from components.cards import CardFrame, MetricCard, StatusBanner
from components.memory_visualization import MemoryBlockCanvas
from config import COLORS, FONTS


class MemoryAllocationPage(ctk.CTkFrame):
    """Interactive Memory Allocation module backed by C++ first_fit, best_fit, worst_fit, and compare_allocation."""

    ALGO_LABELS = {
        "First Fit": "first_fit",
        "Best Fit": "best_fit",
        "Worst Fit": "worst_fit",
    }

    def __init__(self, master: Any, bridge: BackendBridge, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge = bridge

        # State lists (initial partition blocks optional; processes list)
        self._initial_blocks: List[Dict[str, Any]] = []
        self._processes: List[Dict[str, Any]] = [
            {"process_id": "P1", "size": 212},
            {"process_id": "P2", "size": 417},
            {"process_id": "P3", "size": 112},
            {"process_id": "P4", "size": 426},
        ]

        self.banner = StatusBanner(self)
        self._build_ui()
        self._refresh_block_list_ui()
        self._refresh_process_list_ui()

    def _build_ui(self) -> None:
        # Top Configuration & Process Queue Grid
        top_grid = ctk.CTkFrame(self, fg_color="transparent")
        top_grid.pack(fill="x", pady=(0, 14))
        top_grid.grid_columnconfigure(0, weight=1, uniform="alloc_top")
        top_grid.grid_columnconfigure(1, weight=1, uniform="alloc_top")

        # Left Card: Memory & Optional Initial Partitions
        mem_card = CardFrame(
            top_grid,
            title="1. Memory & Initial Partition Configuration",
            subtitle="Supports fixed partitions or single free pool",
        )
        mem_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tm_row = ctk.CTkFrame(mem_card, fg_color="transparent")
        tm_row.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(
            tm_row,
            text="Total Memory Size (KB):",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        self.total_mem_entry = ctk.CTkEntry(
            tm_row,
            width=140,
            height=34,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["mono_bold"],
        )
        self.total_mem_entry.insert(0, "1024")
        self.total_mem_entry.pack(side="right")

        # Optional Initial Memory Blocks builder
        part_hdr = ctk.CTkFrame(mem_card, fg_color="transparent")
        part_hdr.pack(fill="x", padx=16, pady=(2, 4))
        ctk.CTkLabel(
            part_hdr,
            text="Initial Memory Blocks (Optional — leave empty for 1 contiguous free block):",
            font=FONTS["small_bold"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(side="left")

        part_inputs = ctk.CTkFrame(mem_card, fg_color=COLORS["card_alt_bg"], corner_radius=10)
        part_inputs.pack(fill="x", padx=16, pady=(0, 8))

        self.blk_start_entry = ctk.CTkEntry(
            part_inputs,
            placeholder_text="Start Addr",
            width=92,
            height=32,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["small"],
        )
        self.blk_start_entry.pack(side="left", padx=(8, 4), pady=8)

        self.blk_size_entry = ctk.CTkEntry(
            part_inputs,
            placeholder_text="Size (KB)",
            width=92,
            height=32,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["small"],
        )
        self.blk_size_entry.pack(side="left", padx=4, pady=8)

        self.blk_status_menu = ctk.CTkOptionMenu(
            part_inputs,
            values=["free", "allocated"],
            width=105,
            height=32,
            fg_color=COLORS["primary_soft"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_primary"],
            font=FONTS["small_bold"],
        )
        self.blk_status_menu.set("free")
        self.blk_status_menu.pack(side="left", padx=4, pady=8)

        SecondaryButton(
            part_inputs,
            text="+ Block",
            width=82,
            height=32,
            command=self._add_initial_block,
        ).pack(side="right", padx=(4, 8), pady=8)

        self.blocks_list_frame = ctk.CTkScrollableFrame(
            mem_card,
            height=115,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=8,
        )
        self.blocks_list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Right Card: Process Allocation Queue
        proc_card = CardFrame(
            top_grid,
            title="2. Process Allocation Requests",
            subtitle="Add or remove processes to allocate",
        )
        proc_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        add_row = ctk.CTkFrame(proc_card, fg_color=COLORS["card_alt_bg"], corner_radius=10)
        add_row.pack(fill="x", padx=16, pady=(4, 8))

        self.proc_id_entry = ctk.CTkEntry(
            add_row,
            placeholder_text="Process ID (e.g. P5)",
            width=145,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
        )
        self.proc_id_entry.pack(side="left", padx=(10, 6), pady=8)

        self.proc_size_entry = ctk.CTkEntry(
            add_row,
            placeholder_text="Size (KB)",
            width=115,
            height=34,
            fg_color="#FFFFFF",
            border_color=COLORS["border_strong"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
        )
        self.proc_size_entry.pack(side="left", padx=6, pady=8)

        PrimaryButton(
            add_row,
            text="+ Add Process",
            width=125,
            height=34,
            command=self._add_process,
        ).pack(side="right", padx=(6, 10), pady=8)

        self.proc_list_frame = ctk.CTkScrollableFrame(
            proc_card,
            height=155,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=8,
        )
        self.proc_list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Control Bar
        ctrl_card = CardFrame(self)
        ctrl_card.pack(fill="x", pady=(0, 14))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            ctrl_inner,
            text="Algorithm:",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 8))

        self.algo_selector = ctk.CTkSegmentedButton(
            ctrl_inner,
            values=["First Fit", "Best Fit", "Worst Fit"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["primary_soft"],
            unselected_hover_color=COLORS["primary_light"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_bold"],
            height=36,
        )
        self.algo_selector.set("First Fit")
        self.algo_selector.pack(side="left", padx=(0, 14))

        self.run_btn = PrimaryButton(
            ctrl_inner,
            text="▶  Run Simulation",
            width=165,
            command=self._run_single,
        )
        self.run_btn.pack(side="left", padx=4)

        self.run_all_btn = SecondaryButton(
            ctrl_inner,
            text="⚡ Run All Algorithms",
            width=180,
            command=self._run_all,
        )
        self.run_all_btn.pack(side="left", padx=4)

        NeutralButton(
            ctrl_inner,
            text="Reset",
            width=95,
            command=self._reset,
        ).pack(side="right")

        # KPI Metrics Row
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 14))
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="alloc_kpi")

        self.kpi_allocated = MetricCard(kpi_row, "Allocated Memory", "0 KB", COLORS["primary"], "Total assigned bytes")
        self.kpi_allocated.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.kpi_free = MetricCard(kpi_row, "Remaining Free Memory", "0 KB", COLORS["secondary"], "Unallocated capacity")
        self.kpi_free.grid(row=0, column=1, sticky="nsew", padx=6)

        self.kpi_util = MetricCard(kpi_row, "Memory Utilization", "0.0%", COLORS["success"], "Allocated / Total Memory")
        self.kpi_util.grid(row=0, column=2, sticky="nsew", padx=6)

        self.kpi_frag = MetricCard(kpi_row, "Internal Fragmentation", "0 KB", COLORS["accent_indigo"], "Reported by backend")
        self.kpi_frag.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # Graphical Memory Layout Card
        vis_card = CardFrame(
            self,
            title="Graphical Memory Block Layout",
            subtitle="Proportional partition map with start/end addresses",
        )
        vis_card.pack(fill="x", pady=(0, 14))

        self.memory_canvas = MemoryBlockCanvas(vis_card, canvas_height=134)
        self.memory_canvas.pack(fill="x", padx=16, pady=(4, 14))

        # All-Algorithms Quick Summary Card (hidden until Run All Algorithms is clicked)
        self.all_algos_card = CardFrame(
            self,
            title="All Algorithms Side-by-Side Summary (Identical Input)",
            subtitle="First Fit vs Best Fit vs Worst Fit",
        )
        self.all_algos_container = ctk.CTkFrame(self.all_algos_card, fg_color="transparent")
        self.all_algos_container.pack(fill="x", padx=16, pady=(4, 14))
        self._all_card_visible = False

        # Process Allocation Status & Log Table
        res_card = CardFrame(
            self,
            title="Process Allocation Results & Step Log",
            subtitle="Per-process outcome returned by C++ engine",
        )
        res_card.pack(fill="x", pady=(0, 10))

        self.results_table_frame = ctk.CTkFrame(res_card, fg_color="transparent")
        self.results_table_frame.pack(fill="x", padx=16, pady=(4, 14))
        self._render_empty_results()

    def _add_initial_block(self) -> None:
        self.banner.hide()
        try:
            start_addr = int(self.blk_start_entry.get().strip())
            size_val = int(self.blk_size_entry.get().strip())
            total_mem = int(self.total_mem_entry.get().strip())
        except ValueError:
            self.banner.show_error("Start address, block size, and total memory must be valid integers.")
            return

        if start_addr < 0 or size_val <= 0 or total_mem <= 0:
            self.banner.show_error("Start address must be >= 0 and sizes must be > 0.")
            return
        if start_addr + size_val > total_mem:
            self.banner.show_error("Initial block exceeds Total Memory.")
            return

        status = self.blk_status_menu.get()
        block_entry: Dict[str, Any] = {
            "id": len(self._initial_blocks) + 1,
            "status": status,
            "start_address": start_addr,
            "size": size_val,
        }
        if status == "allocated":
            block_entry["process_id"] = f"SYS_{len(self._initial_blocks) + 1}"
            block_entry["requested_size"] = size_val

        self._initial_blocks.append(block_entry)
        self.blk_start_entry.delete(0, "end")
        self.blk_size_entry.delete(0, "end")
        self._refresh_block_list_ui()

    def _remove_initial_block(self, index: int) -> None:
        if 0 <= index < len(self._initial_blocks):
            self._initial_blocks.pop(index)
            for idx, blk in enumerate(self._initial_blocks, start=1):
                blk["id"] = idx
            self._refresh_block_list_ui()

    def _refresh_block_list_ui(self) -> None:
        for child in self.blocks_list_frame.winfo_children():
            child.destroy()

        if not self._initial_blocks:
            ctk.CTkLabel(
                self.blocks_list_frame,
                text="No custom partitions added — entire Total Memory starts as a single free block.",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(pady=24)
            return

        for idx, blk in enumerate(self._initial_blocks):
            row = ctk.CTkFrame(self.blocks_list_frame, fg_color="#FFFFFF", corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            badge_bg = COLORS["primary_soft"] if blk["status"] == "free" else COLORS["warning_bg"]
            badge_fg = COLORS["primary"] if blk["status"] == "free" else COLORS["warning"]

            ctk.CTkLabel(
                row,
                text=f"Block #{blk['id']}  |  Addr: {blk['start_address']}..{blk['start_address'] + blk['size']}  |  Size: {blk['size']} KB",
                font=FONTS["mono"],
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=10, pady=5)

            ctk.CTkLabel(
                row,
                text=blk["status"].upper(),
                font=FONTS["caption"],
                fg_color=badge_bg,
                text_color=badge_fg,
                corner_radius=5,
                padx=6,
                pady=2,
            ).pack(side="left", padx=6)

            DangerButton(
                row,
                text="Remove",
                width=74,
                height=26,
                command=lambda i=idx: self._remove_initial_block(i),
            ).pack(side="right", padx=8, pady=4)

    def _add_process(self) -> None:
        self.banner.hide()
        pid = self.proc_id_entry.get().strip()
        raw_size = self.proc_size_entry.get().strip()

        if not pid:
            self.banner.show_error("Please enter a Process ID (e.g., P5).")
            return
        try:
            size_val = int(raw_size)
        except ValueError:
            self.banner.show_error("Process size must be a positive integer.")
            return
        if size_val <= 0:
            self.banner.show_error("Process size must be greater than 0.")
            return

        self._processes.append({"process_id": pid, "size": size_val})
        self.proc_id_entry.delete(0, "end")
        self.proc_size_entry.delete(0, "end")
        self._refresh_process_list_ui()

    def _remove_process(self, index: int) -> None:
        if 0 <= index < len(self._processes):
            self._processes.pop(index)
            self._refresh_process_list_ui()

    def _refresh_process_list_ui(self) -> None:
        for child in self.proc_list_frame.winfo_children():
            child.destroy()

        if not self._processes:
            ctk.CTkLabel(
                self.proc_list_frame,
                text="Process queue is empty. Add processes above to simulate allocation.",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
            ).pack(pady=36)
            return

        for idx, proc in enumerate(self._processes):
            row = ctk.CTkFrame(self.proc_list_frame, fg_color="#FFFFFF", corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            ctk.CTkLabel(
                row,
                text=f"#{idx + 1}",
                font=FONTS["small_bold"],
                text_color=COLORS["text_muted"],
                width=30,
            ).pack(side="left", padx=(8, 4), pady=5)

            ctk.CTkLabel(
                row,
                text=proc["process_id"],
                font=FONTS["body_bold"],
                text_color=COLORS["primary"],
                width=90,
                anchor="w",
            ).pack(side="left", padx=4)

            ctk.CTkLabel(
                row,
                text=f"Requested Size: {proc['size']} KB",
                font=FONTS["mono"],
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=8)

            DangerButton(
                row,
                text="Remove",
                width=76,
                height=26,
                command=lambda i=idx: self._remove_process(i),
            ).pack(side="right", padx=8, pady=4)

    def _collect_payload(self) -> Optional[Dict[str, Any]]:
        try:
            total_memory = int(self.total_mem_entry.get().strip())
        except ValueError:
            self.banner.show_error("Total Memory must be a valid positive integer.")
            return None

        if total_memory <= 0:
            self.banner.show_error("Total Memory must be greater than 0.")
            return None

        if not self._processes:
            self.banner.show_error("Add at least one process request before running the simulation.")
            return None

        return {
            "total_memory": total_memory,
            "initial_blocks": list(self._initial_blocks),
            "requests": list(self._processes),
        }

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.run_btn.configure(state=state)
        self.run_all_btn.configure(state=state)

    def _run_single(self) -> None:
        self.banner.hide()
        payload = self._collect_payload()
        if payload is None:
            return

        selected_label = self.algo_selector.get()
        operation = self.ALGO_LABELS.get(selected_label, "first_fit")
        self._set_busy(True)

        def on_ok(result: Dict[str, Any]) -> None:
            self._set_busy(False)
            self._hide_all_algos_card()
            self._apply_single_result(result)
            self.banner.show_success(
                f"{selected_label} completed: {result.get('successful_allocations', 0)} allocated, "
                f"{result.get('failed_allocations', 0)} failed."
            )

        def on_err(msg: str) -> None:
            self._set_busy(False)
            self.banner.show_error(msg)

        self.bridge.execute_async(self, operation, payload, on_ok, on_err)

    def _run_all(self) -> None:
        self.banner.hide()
        payload = self._collect_payload()
        if payload is None:
            return

        self._set_busy(True)

        def on_ok(result: Dict[str, Any]) -> None:
            self._set_busy(False)
            selected_key = self.ALGO_LABELS.get(self.algo_selector.get(), "first_fit")
            if selected_key in result:
                self._apply_single_result(result[selected_key])
            self._render_all_algos_summary(result)
            self.banner.show_success("Executed First Fit, Best Fit, and Worst Fit on identical inputs.")

        def on_err(msg: str) -> None:
            self._set_busy(False)
            self.banner.show_error(msg)

        self.bridge.execute_async(self, "compare_allocation", payload, on_ok, on_err)

    def _apply_single_result(self, res: Dict[str, Any]) -> None:
        total_mem = int(res.get("total_memory", 0))
        alloc_mem = int(res.get("allocated_memory", 0))
        free_mem = int(res.get("free_memory", 0))
        util = float(res.get("memory_utilization", 0.0))
        frag = int(res.get("total_internal_fragmentation", 0))
        succ = int(res.get("successful_allocations", 0))
        fail = int(res.get("failed_allocations", 0))

        self.kpi_allocated.set_value(f"{alloc_mem} KB", f"{succ} process(es) allocated")
        self.kpi_free.set_value(f"{free_mem} KB", f"Out of {total_mem} KB total")
        self.kpi_util.set_value(f"{util:.2f}%", f"{fail} failed request(s)")
        self.kpi_frag.set_value(f"{frag} KB", "Total internal fragmentation")

        self.memory_canvas.set_data(total_mem, res.get("memory_blocks", []))
        self._render_results_table(res.get("results", []))

    def _render_all_algos_summary(self, comp: Dict[str, Any]) -> None:
        for child in self.all_algos_container.winfo_children():
            child.destroy()

        grid = ctk.CTkFrame(self.all_algos_container, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="all_alloc")

        for col_idx, (title, key) in enumerate(
            [("First Fit", "first_fit"), ("Best Fit", "best_fit"), ("Worst Fit", "worst_fit")]
        ):
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

            lines = [
                f"Allocated: {data.get('allocated_memory', 0)} / {data.get('total_memory', 0)} KB",
                f"Free Memory: {data.get('free_memory', 0)} KB",
                f"Utilization: {float(data.get('memory_utilization', 0.0)):.2f}%",
                f"Success / Failed: {data.get('successful_allocations', 0)} / {data.get('failed_allocations', 0)}",
                f"Internal Frag: {data.get('total_internal_fragmentation', 0)} KB",
            ]
            for line in lines:
                ctk.CTkLabel(
                    box,
                    text=line,
                    font=FONTS["small"],
                    text_color=COLORS["text_primary"],
                    anchor="w",
                ).pack(fill="x", padx=12, pady=1)

            ctk.CTkFrame(box, height=8, fg_color="transparent").pack()

        if not self._all_card_visible:
            self.all_algos_card.pack(fill="x", pady=(0, 14))
            self._all_card_visible = True

    def _hide_all_algos_card(self) -> None:
        if self._all_card_visible:
            self.all_algos_card.pack_forget()
            self._all_card_visible = False

    def _render_empty_results(self) -> None:
        for child in self.results_table_frame.winfo_children():
            child.destroy()
        ctk.CTkLabel(
            self.results_table_frame,
            text="No allocation simulation executed yet. Configure memory and click 'Run Simulation'.",
            font=FONTS["subtitle"],
            text_color=COLORS["text_muted"],
        ).pack(pady=18)

    def _render_results_table(self, entries: List[Dict[str, Any]]) -> None:
        for child in self.results_table_frame.winfo_children():
            child.destroy()

        headers = ["Process", "Requested", "Status", "Block ID", "Start Addr", "Block Size", "Frag.", "Backend Log / Reason"]
        widths = [85, 95, 105, 80, 95, 95, 75, 340]

        hdr_row = ctk.CTkFrame(self.results_table_frame, fg_color=COLORS["table_header_bg"], corner_radius=8)
        hdr_row.pack(fill="x", pady=(0, 4))
        for title, w in zip(headers, widths):
            ctk.CTkLabel(
                hdr_row,
                text=title,
                width=w,
                font=FONTS["small_bold"],
                text_color=COLORS["primary"],
                anchor="w",
            ).pack(side="left", padx=6, pady=7)

        for idx, item in enumerate(entries):
            allocated = bool(item.get("allocated", False))
            row_bg = COLORS["table_row_even"] if idx % 2 == 0 else COLORS["table_row_odd"]
            if not allocated:
                row_bg = COLORS["danger_bg"]

            row = ctk.CTkFrame(
                self.results_table_frame,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=COLORS["danger_border"] if not allocated else COLORS["divider"],
            )
            row.pack(fill="x", pady=2)

            status_text = "ALLOCATED" if allocated else "FAILED"
            status_fg = COLORS["success"] if allocated else COLORS["danger"]

            vals = [
                str(item.get("process_id", "")),
                f"{item.get('requested_size', 0)} KB",
                status_text,
                str(item.get("block_id", -1)) if allocated else "—",
                str(item.get("start_address", 0)) if allocated else "—",
                f"{item.get('block_size', 0)} KB" if allocated else "—",
                f"{item.get('internal_fragmentation', 0)} KB" if allocated else "—",
                str(item.get("reason", "")),
            ]

            for col_i, (val, w) in enumerate(zip(vals, widths)):
                ctk.CTkLabel(
                    row,
                    text=val,
                    width=w,
                    font=FONTS["small_bold"] if col_i in (0, 2) else FONTS["small"],
                    text_color=status_fg if col_i == 2 else COLORS["text_primary"],
                    anchor="w",
                ).pack(side="left", padx=6, pady=6)

    def _reset(self) -> None:
        self.banner.hide()
        self.total_mem_entry.delete(0, "end")
        self.total_mem_entry.insert(0, "1024")
        self._initial_blocks.clear()
        self._processes = [
            {"process_id": "P1", "size": 212},
            {"process_id": "P2", "size": 417},
            {"process_id": "P3", "size": 112},
            {"process_id": "P4", "size": 426},
        ]
        self._refresh_block_list_ui()
        self._refresh_process_list_ui()

        self.kpi_allocated.set_value("0 KB", "Total assigned bytes")
        self.kpi_free.set_value("0 KB", "Unallocated capacity")
        self.kpi_util.set_value("0.0%", "Allocated / Total Memory")
        self.kpi_frag.set_value("0 KB", "Reported by backend")

        self.memory_canvas.clear()
        self._hide_all_algos_card()
        self._render_empty_results()
