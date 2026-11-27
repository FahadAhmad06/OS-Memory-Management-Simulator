"""Graphical contiguous memory block visualizer and process allocation status display."""

from __future__ import annotations

import tkinter as tk
from typing import Any, Dict, List
import customtkinter as ctk

from config import COLORS, FONTS, PROCESS_PALETTE


class MemoryBlockCanvas(ctk.CTkFrame):
    """Renders proportional contiguous memory partitions with process colors, addresses, and sizes."""

    def __init__(self, master: Any, canvas_height: int = 128, **kwargs: Any) -> None:
        super().__init__(
            master,
            fg_color=COLORS["card_alt_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._blocks: List[Dict[str, Any]] = []
        self._total_memory: int = 0
        self._process_colors: Dict[str, str] = {}

        self.canvas = tk.Canvas(
            self,
            height=canvas_height,
            bg=COLORS["card_alt_bg"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="x", expand=True, padx=12, pady=(10, 6))
        self.canvas.bind("<Configure>", lambda _e: self._redraw())

        self.legend_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.legend_frame.pack(fill="x", padx=12, pady=(0, 10))

        self._draw_placeholder()

    def set_data(self, total_memory: int, blocks: List[Dict[str, Any]]) -> None:
        self._total_memory = max(0, int(total_memory))
        self._blocks = list(blocks)
        self._assign_process_colors()
        self._redraw()
        self._rebuild_legend()

    def clear(self) -> None:
        self._blocks = []
        self._total_memory = 0
        self._process_colors = {}
        self._draw_placeholder()
        for child in self.legend_frame.winfo_children():
            child.destroy()

    def _assign_process_colors(self) -> None:
        self._process_colors.clear()
        idx = 0
        for blk in self._blocks:
            if blk.get("status") == "allocated":
                pid = str(blk.get("process_id", "")).strip() or f"B{blk.get('id', idx)}"
                if pid not in self._process_colors:
                    self._process_colors[pid] = PROCESS_PALETTE[idx % len(PROCESS_PALETTE)]
                    idx += 1

    def _draw_placeholder(self) -> None:
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 560)
        h = max(self.canvas.winfo_height(), 120)
        self.canvas.create_rectangle(
            10,
            24,
            w - 10,
            h - 32,
            fill=COLORS["empty_frame_bg"],
            outline=COLORS["border_strong"],
            dash=(5, 4),
            width=2,
        )
        self.canvas.create_text(
            w // 2,
            (h - 8) // 2,
            text="Run simulation to render memory partitions",
            fill=COLORS["text_muted"],
            font=("Segoe UI", 11, "italic"),
        )

    def _redraw(self) -> None:
        if not self._blocks or self._total_memory <= 0:
            self._draw_placeholder()
            return

        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 560)
        h = max(self.canvas.winfo_height(), 124)

        left_pad = 12
        right_pad = 12
        usable_w = max(120, w - left_pad - right_pad)
        top_y = 22
        bottom_y = h - 34

        # Enforce minimum visual width so tiny blocks remain legible while preserving proportional scale
        n = len(self._blocks)
        min_seg_w = min(44, max(18, usable_w // max(n * 2, 1)))
        raw_widths = [
            max(min_seg_w, (float(blk.get("size", 0)) / float(self._total_memory)) * usable_w)
            for blk in self._blocks
        ]
        scale = usable_w / sum(raw_widths) if sum(raw_widths) > 0 else 1.0
        widths = [rw * scale for rw in raw_widths]

        curr_x = float(left_pad)
        for idx, blk in enumerate(self._blocks):
            seg_w = widths[idx]
            x1 = int(round(curr_x))
            x2 = int(round(curr_x + seg_w))
            if idx == n - 1:
                x2 = left_pad + usable_w

            status = blk.get("status", "free")
            size_val = blk.get("size", 0)
            start_addr = blk.get("start_address", 0)
            end_addr = start_addr + size_val

            if status == "allocated":
                pid = str(blk.get("process_id", "")).strip() or f"Blk {blk.get('id', idx + 1)}"
                fill_color = self._process_colors.get(pid, COLORS["primary"])
                outline_color = "#FFFFFF"
                text_color = "#FFFFFF"
                title_text = pid
            else:
                fill_color = COLORS["free_block_bg"]
                outline_color = COLORS["free_block_border"]
                text_color = COLORS["free_block_text"]
                title_text = "FREE"

            self.canvas.create_rectangle(
                x1,
                top_y,
                x2,
                bottom_y,
                fill=fill_color,
                outline=outline_color,
                width=2,
            )

            center_x = (x1 + x2) // 2
            mid_y = (top_y + bottom_y) // 2

            if (x2 - x1) >= 42:
                self.canvas.create_text(
                    center_x,
                    mid_y - 10,
                    text=title_text,
                    fill=text_color,
                    font=("Segoe UI", 10, "bold"),
                )
                self.canvas.create_text(
                    center_x,
                    mid_y + 10,
                    text=f"{size_val} KB",
                    fill=text_color,
                    font=("Segoe UI", 9, "normal"),
                )
            elif (x2 - x1) >= 22:
                self.canvas.create_text(
                    center_x,
                    mid_y,
                    text=title_text[:4],
                    fill=text_color,
                    font=("Segoe UI", 8, "bold"),
                )

            # Start address tick
            if idx == 0 or (x2 - x1) >= 46:
                self.canvas.create_text(
                    x1,
                    bottom_y + 14,
                    text=str(start_addr),
                    fill=COLORS["text_muted"],
                    font=("DejaVu Sans Mono", 8, "normal"),
                    anchor="w" if idx == 0 else "center",
                )

            if idx == n - 1:
                self.canvas.create_text(
                    x2,
                    bottom_y + 14,
                    text=str(end_addr),
                    fill=COLORS["text_muted"],
                    font=("DejaVu Sans Mono", 8, "normal"),
                    anchor="e",
                )

            curr_x += seg_w

    def _rebuild_legend(self) -> None:
        for child in self.legend_frame.winfo_children():
            child.destroy()

        # Free memory chip
        free_chip = ctk.CTkLabel(
            self.legend_frame,
            text=" ■ Free Memory ",
            font=FONTS["caption"],
            fg_color=COLORS["free_block_bg"],
            text_color=COLORS["free_block_text"],
            corner_radius=6,
            padx=6,
            pady=2,
        )
        free_chip.pack(side="left", padx=(0, 6))

        for pid, color in self._process_colors.items():
            chip = ctk.CTkLabel(
                self.legend_frame,
                text=f" ■ {pid} ",
                font=FONTS["caption"],
                fg_color=color,
                text_color="#FFFFFF",
                corner_radius=6,
                padx=6,
                pady=2,
            )
            chip.pack(side="left", padx=(0, 6))
