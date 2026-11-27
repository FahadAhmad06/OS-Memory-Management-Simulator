"""Home dashboard page with hero banner, module cards, summary stats, and quick navigation."""

from __future__ import annotations

from typing import Any, Callable
import customtkinter as ctk

from assets.icons.generator import create_module_illustration
from components.buttons import PrimaryButton, SecondaryButton
from components.cards import CardFrame, MetricCard
from config import COLORS, DEPARTMENT_NAME, FONTS, UNIVERSITY_NAME


class HomePage(ctk.CTkFrame):
    """Landing dashboard introducing the simulator and providing one-click module navigation."""

    def __init__(
        self,
        master: Any,
        on_navigate: Callable[[str], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_navigate = on_navigate
        self._illustrations: list[ctk.CTkImage] = []
        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Hero Welcome Banner
        hero = ctk.CTkFrame(
            self,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border_strong"],
        )
        hero.pack(fill="x", pady=(0, 16))

        top_strip = ctk.CTkFrame(
            hero,
            fg_color=COLORS["primary"],
            corner_radius=12,
        )
        top_strip.pack(fill="x", padx=14, pady=(14, 12))

        strip_content = ctk.CTkFrame(top_strip, fg_color="transparent")
        strip_content.pack(fill="x", padx=20, pady=18)

        uvas_badge = ctk.CTkLabel(
            strip_content,
            text=f"🎓  {UNIVERSITY_NAME}  •  {DEPARTMENT_NAME}",
            font=FONTS["small_bold"],
            fg_color="#1E40AF",
            text_color="#DBEAFE",
            corner_radius=8,
            padx=12,
            pady=4,
        )
        uvas_badge.pack(anchor="w")

        ctk.CTkLabel(
            strip_content,
            text="OS Memory Management Simulator",
            font=FONTS["hero_title"],
            text_color="#FFFFFF",
            anchor="w",
        ).pack(anchor="w", pady=(10, 2))

        ctk.CTkLabel(
            strip_content,
            text="Visualize, Analyze, Understand",
            font=("Segoe UI", 14, "bold"),
            text_color="#BFDBFE",
            anchor="w",
        ).pack(anchor="w")

        # Welcome section
        welcome_body = ctk.CTkFrame(hero, fg_color="transparent")
        welcome_body.pack(fill="x", padx=22, pady=(4, 18))

        ctk.CTkLabel(
            welcome_body,
            text="Welcome to Our Project!",
            font=FONTS["section_title"],
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            welcome_body,
            text=(
                "An educational simulator to visualize and understand memory management concepts "
                "in Operating Systems. Powered by a compiled C++17 simulation engine and an interactive "
                "Python desktop interface."
            ),
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=980,
            justify="left",
        ).pack(anchor="w", pady=(4, 12))

        quick_row = ctk.CTkFrame(welcome_body, fg_color="transparent")
        quick_row.pack(anchor="w")

        PrimaryButton(
            quick_row,
            text="Open Algorithm Comparison",
            width=220,
            command=lambda: self._on_navigate("comparison"),
        ).pack(side="left", padx=(0, 10))

        SecondaryButton(
            quick_row,
            text="About Project & Team",
            width=185,
            command=lambda: self._on_navigate("about"),
        ).pack(side="left")

        # 2. Project Summary KPI Row
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 16))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        m1 = MetricCard(
            stats_row,
            label="Total Modules",
            initial_value="3",
            accent_color=COLORS["primary"],
            subtext="Memory Allocation, Paging, Page Replacement",
        )
        m1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        m2 = MetricCard(
            stats_row,
            label="Total Individual Algorithms",
            initial_value="7",
            accent_color=COLORS["secondary"],
            subtext="First/Best/Worst Fit, Paging, FIFO, LRU, Optimal",
        )
        m2.grid(row=0, column=1, sticky="nsew", padx=8)

        m3 = MetricCard(
            stats_row,
            label="Team Members",
            initial_value="3",
            accent_color=COLORS["accent_indigo"],
            subtext="BSCS Team — UVAS Lahore",
        )
        m3.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # 3. Three Core Simulator Module Cards
        ctk.CTkLabel(
            self,
            text="Core Simulation Modules",
            font=FONTS["section_title"],
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(2, 10))

        modules_grid = ctk.CTkFrame(self, fg_color="transparent")
        modules_grid.pack(fill="x", pady=(0, 12))
        modules_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="modules")

        module_specs = [
            {
                "col": 0,
                "title": "Memory Allocation",
                "badge": "Contiguous Partitions",
                "illus": "allocation",
                "desc": "Simulate dynamic contiguous partition placement and inspect free space and utilization.",
                "bullets": ["First Fit", "Best Fit", "Worst Fit"],
                "target": "memory_allocation",
            },
            {
                "col": 1,
                "title": "Paging",
                "badge": "Address Translation",
                "illus": "paging",
                "desc": "Translate logical addresses into physical frame addresses using page tables and offsets.",
                "bullets": ["Logical Address", "Page Table", "Physical Address"],
                "target": "paging",
            },
            {
                "col": 2,
                "title": "Page Replacement",
                "badge": "Virtual Memory",
                "illus": "replacement",
                "desc": "Trace frame-by-frame page faults, page hits, and victim evictions across reference strings.",
                "bullets": ["FIFO", "LRU", "Optimal"],
                "target": "page_replacement",
            },
        ]

        for spec in module_specs:
            pad_l = 0 if spec["col"] == 0 else 8
            pad_r = 0 if spec["col"] == 2 else 8
            card = CardFrame(modules_grid)
            card.grid(row=0, column=spec["col"], sticky="nsew", padx=(pad_l, pad_r))

            top_tag = ctk.CTkLabel(
                card,
                text=spec["badge"],
                font=FONTS["caption"],
                fg_color=COLORS["primary_soft"],
                text_color=COLORS["primary"],
                corner_radius=6,
                padx=8,
                pady=3,
            )
            top_tag.pack(anchor="w", padx=16, pady=(14, 6))

            ctk.CTkLabel(
                card,
                text=spec["title"],
                font=("Segoe UI", 16, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(fill="x", padx=16)

            illus_img = create_module_illustration(spec["illus"], width=270, height=82)
            self._illustrations.append(illus_img)
            ctk.CTkLabel(card, text="", image=illus_img).pack(padx=16, pady=(10, 8))

            ctk.CTkLabel(
                card,
                text=spec["desc"],
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w",
                wraplength=280,
                justify="left",
            ).pack(fill="x", padx=16, pady=(0, 8))

            for item in spec["bullets"]:
                row = ctk.CTkFrame(card, fg_color=COLORS["card_alt_bg"], corner_radius=7)
                row.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(
                    row,
                    text=f"  •  {item}",
                    font=FONTS["small_bold"],
                    text_color=COLORS["text_primary"],
                    anchor="w",
                ).pack(fill="x", padx=8, pady=4)

            PrimaryButton(
                card,
                text="Open Simulator →",
                width=200,
                command=lambda t=spec["target"]: self._on_navigate(t),
            ).pack(fill="x", padx=16, pady=(14, 16))
