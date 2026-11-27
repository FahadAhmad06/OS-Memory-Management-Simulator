"""About page featuring project overview, objectives, technologies, and BSCS team profile cards."""

from __future__ import annotations

from typing import Any
import customtkinter as ctk

from assets.icons.generator import create_developer_avatar
from components.cards import CardFrame
from config import COLORS, DEPARTMENT_NAME, FONTS, UNIVERSITY_NAME


class AboutPage(ctk.CTkFrame):
    """Project documentation and team credits page."""

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._avatars: list[ctk.CTkImage] = []
        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Project Overview Card
        overview_card = CardFrame(
            self,
            title="Project Overview",
            subtitle=f"{UNIVERSITY_NAME} • {DEPARTMENT_NAME}",
        )
        overview_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            overview_card,
            text="OS Memory Management Simulator",
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(fill="x", padx=16, pady=(2, 4))

        ctk.CTkLabel(
            overview_card,
            text=(
                "An educational team project developed by BSCS students of the University of Veterinary "
                "and Animal Sciences, Lahore, to understand and visualize memory management concepts in "
                "Operating Systems. The application combines a deterministic C++17 simulation backend "
                "with a modern, interactive Python CustomTkinter desktop interface."
            ),
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=980,
            justify="left",
        ).pack(fill="x", padx=16, pady=(0, 14))

        # 2. Our Team Section (All three members wear glasses; Muhammad Afnan highlighted as Team Leader)
        team_card = CardFrame(
            self,
            title="Our Team",
            subtitle="BSCS Students — University of Veterinary and Animal Sciences (UVAS), Lahore",
        )
        team_card.pack(fill="x", pady=(0, 14))

        team_grid = ctk.CTkFrame(team_card, fg_color="transparent")
        team_grid.pack(fill="x", padx=16, pady=(6, 16))
        team_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="team_cols")

        members = [
            {
                "name": "Muhammad Afnan",
                "role": "Team Leader",
                "initials": "MA",
                "is_leader": True,
                "accent": "#1D4ED8",
                "desc": "Project architecture, simulation integration, and team coordination.",
            },
            {
                "name": "Fahad Ahmad",
                "role": "Developer",
                "initials": "FA",
                "is_leader": False,
                "accent": "#0284C7",
                "desc": "Core algorithm implementation, backend-frontend bridge, and GUI engineering.",
            },
            {
                "name": "Subhan Khan",
                "role": "Developer",
                "initials": "SK",
                "is_leader": False,
                "accent": "#4F46E5",
                "desc": "Visualization components, comparative analytics, and simulation testing.",
            },
        ]

        for idx, member in enumerate(members):
            is_leader = bool(member["is_leader"])
            card_bg = COLORS["primary_soft"] if is_leader else COLORS["card_alt_bg"]
            border_col = COLORS["primary"] if is_leader else COLORS["border_strong"]
            border_w = 2 if is_leader else 1

            p_card = ctk.CTkFrame(
                team_grid,
                fg_color=card_bg,
                corner_radius=14,
                border_width=border_w,
                border_color=border_col,
            )
            p_card.grid(row=0, column=idx, sticky="nsew", padx=6)

            badge_bg = COLORS["primary"] if is_leader else COLORS["primary_light"]
            badge_fg = "#FFFFFF" if is_leader else COLORS["primary"]
            badge_text = "★  TEAM LEADER" if is_leader else "DEVELOPER"

            ctk.CTkLabel(
                p_card,
                text=badge_text,
                font=("Segoe UI", 10, "bold"),
                fg_color=badge_bg,
                text_color=badge_fg,
                corner_radius=7,
                padx=10,
                pady=3,
            ).pack(pady=(14, 8))

            avatar_img = create_developer_avatar(
                initials=member["initials"],
                accent_color=member["accent"],
                is_leader=is_leader,
                size=96,
            )
            self._avatars.append(avatar_img)

            ctk.CTkLabel(p_card, text="", image=avatar_img).pack(pady=(2, 8))

            ctk.CTkLabel(
                p_card,
                text=member["name"],
                font=("Segoe UI", 16, "bold"),
                text_color=COLORS["text_primary"],
            ).pack()

            ctk.CTkLabel(
                p_card,
                text=f"Role: {member['role']}",
                font=FONTS["body_bold"],
                text_color=COLORS["primary"] if is_leader else COLORS["secondary"],
            ).pack(pady=(2, 4))

            ctk.CTkLabel(
                p_card,
                text="Education: BSCS Student\nUniversity: UVAS Lahore",
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                justify="center",
            ).pack(pady=(0, 6))

            ctk.CTkLabel(
                p_card,
                text=member["desc"],
                font=FONTS["caption"],
                text_color=COLORS["text_muted"],
                wraplength=260,
                justify="center",
            ).pack(padx=14, pady=(0, 14))

        # 3. Project Objectives & Key Features (Two-column layout)
        mid_grid = ctk.CTkFrame(self, fg_color="transparent")
        mid_grid.pack(fill="x", pady=(0, 14))
        mid_grid.grid_columnconfigure((0, 1), weight=1, uniform="about_mid")

        obj_card = CardFrame(mid_grid, title="Project Objectives")
        obj_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        objectives = [
            "Understand memory allocation strategies (First Fit, Best Fit, Worst Fit).",
            "Understand paging and logical-to-physical address translation.",
            "Understand page replacement algorithms (FIFO, LRU, Optimal).",
            "Visualize memory management states interactively in real time.",
            "Compare algorithm performance across identical workloads.",
            "Improve practical understanding of Operating Systems.",
        ]
        for obj in objectives:
            row = ctk.CTkFrame(obj_card, fg_color=COLORS["card_alt_bg"], corner_radius=8)
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(
                row,
                text=f"✓  {obj}",
                font=FONTS["small"],
                text_color=COLORS["text_primary"],
                anchor="w",
                wraplength=440,
                justify="left",
            ).pack(fill="x", padx=10, pady=6)

        ctk.CTkFrame(obj_card, height=10, fg_color="transparent").pack()

        feat_card = CardFrame(mid_grid, title="Key Features")
        feat_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        features = [
            "Decoupled C++17 simulation core communicating over JSON stdin/stdout.",
            "Proportional memory partition diagrams with process color coding.",
            "Step-by-step paging address decomposition and page fault diagnostics.",
            "Dynamic frame-by-frame timeline with hit, load, and eviction highlights.",
            "Side-by-side comparison dashboards with Matplotlib bar charts.",
            "Non-blocking background execution and clean subprocess lifecycle management.",
        ]
        for feat in features:
            row = ctk.CTkFrame(feat_card, fg_color=COLORS["card_alt_bg"], corner_radius=8)
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(
                row,
                text=f"•  {feat}",
                font=FONTS["small"],
                text_color=COLORS["text_primary"],
                anchor="w",
                wraplength=440,
                justify="left",
            ).pack(fill="x", padx=10, pady=6)

        ctk.CTkFrame(feat_card, height=10, fg_color="transparent").pack()

        # 4. Technologies Used & Our Goal
        bottom_grid = ctk.CTkFrame(self, fg_color="transparent")
        bottom_grid.pack(fill="x", pady=(0, 12))
        bottom_grid.grid_columnconfigure((0, 1), weight=1, uniform="about_bot")

        tech_card = CardFrame(bottom_grid, title="Technologies Used")
        tech_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tech_wrap = ctk.CTkFrame(tech_card, fg_color="transparent")
        tech_wrap.pack(fill="x", padx=16, pady=(4, 16))

        techs = [
            ("C++17", "High-performance simulation backend"),
            ("Python 3", "Desktop application controller"),
            ("CustomTkinter", "Modern light-mode desktop UI"),
            ("Matplotlib", "Comparative analytics charts"),
            ("nlohmann/json", "Structured IPC JSON serialization"),
        ]
        for name, role in techs:
            pill = ctk.CTkFrame(
                tech_wrap,
                fg_color=COLORS["primary_soft"],
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border_strong"],
            )
            pill.pack(fill="x", pady=3)
            ctk.CTkLabel(
                pill,
                text=name,
                font=FONTS["small_bold"],
                text_color=COLORS["primary"],
                width=125,
                anchor="w",
            ).pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(
                pill,
                text=role,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w",
            ).pack(side="left", padx=4, pady=5)

        goal_card = CardFrame(bottom_grid, title="Our Goal")
        goal_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(
            goal_card,
            text=(
                "Operating System memory management algorithms are often taught through static textbook "
                "diagrams that make dynamic trade-offs hard to observe. Our goal is to bridge theory "
                "and intuition by giving students and instructors an immediate, visual, and accurate "
                "laboratory environment where real C++ algorithm executions can be inspected step by step "
                "and compared side by side."
            ),
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=460,
            justify="left",
        ).pack(fill="x", padx=16, pady=(6, 16))
