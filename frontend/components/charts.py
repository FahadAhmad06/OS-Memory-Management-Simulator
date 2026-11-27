"""Embedded Matplotlib light-themed charts for Memory Allocation and Page Replacement comparisons."""

from __future__ import annotations

from typing import Any, Dict, List
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import COLORS


class ComparisonChartWidget(ctk.CTkFrame):
    """Wraps a Matplotlib Figure with light blue/white styling cleanly inside CustomTkinter."""

    def __init__(self, master: Any, figsize: tuple[float, float] = (5.4, 3.2), **kwargs: Any) -> None:
        super().__init__(
            master,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.figure = Figure(figsize=figsize, dpi=100, facecolor="#FFFFFF")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
        self.draw_empty("Run comparison to view chart")

    def draw_empty(self, message: str = "No comparison data available") -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#F8FBFF")
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            fontsize=10,
            color="#64748B",
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#D6E4F7")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_bar_comparison(
        self,
        title: str,
        categories: List[str],
        values: List[float],
        ylabel: str,
        bar_colors: List[str],
        value_suffix: str = "",
        y_max: float | None = None,
    ) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#F8FBFF")

        bars = ax.bar(categories, values, color=bar_colors, width=0.48, edgecolor="#1E3A8A", linewidth=0.6)
        ax.set_title(title, fontsize=11, fontweight="bold", color="#0F172A", pad=12)
        ax.set_ylabel(ylabel, fontsize=9.5, color="#334155")
        ax.tick_params(axis="both", labelsize=9.5, colors="#1E293B")
        ax.grid(axis="y", linestyle="--", alpha=0.55, color="#CBD5E1")
        ax.set_axisbelow(True)

        top_limit = y_max if y_max is not None else (max(values) * 1.24 if values and max(values) > 0 else 10.0)
        ax.set_ylim(0, top_limit)

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color("#94A3B8")

        for bar, val in zip(bars, values):
            formatted = f"{val:.1f}{value_suffix}" if isinstance(val, float) and not val.is_integer() else f"{int(val)}{value_suffix}"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + (top_limit * 0.025),
                formatted,
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color="#0F172A",
            )

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_grouped_allocation_metrics(self, comp_data: Dict[str, Any]) -> None:
        """Plot Memory Utilization (%) and Successful Allocations across First Fit, Best Fit, Worst Fit."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#F8FBFF")

        algos = ["First Fit", "Best Fit", "Worst Fit"]
        keys = ["first_fit", "best_fit", "worst_fit"]
        utilizations = [float(comp_data.get(k, {}).get("memory_utilization", 0.0)) for k in keys]
        colors = ["#1D4ED8", "#0284C7", "#4F46E5"]

        bars = ax.bar(algos, utilizations, color=colors, width=0.46)
        ax.set_title("Memory Utilization Comparison (%)", fontsize=11, fontweight="bold", color="#0F172A", pad=12)
        ax.set_ylabel("Utilization (%)", fontsize=9.5, color="#334155")
        ax.set_ylim(0, 115)
        ax.grid(axis="y", linestyle="--", alpha=0.55, color="#CBD5E1")
        ax.set_axisbelow(True)

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color("#94A3B8")

        for bar, val in zip(bars, utilizations):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 2.5,
                f"{val:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9.5,
                fontweight="bold",
                color="#0F172A",
            )

        self.figure.tight_layout()
        self.canvas.draw_idle()
