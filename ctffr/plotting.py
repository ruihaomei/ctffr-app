"""Radiology-style local-contribution figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from .explain import Explanation


BLUE = "#2c5f8e"
RUST = "#c1553c"


def contribution_plot(explanation: Explanation) -> Figure:
    """Build a restrained top-ten SHAP contribution chart."""
    table = explanation.contributions.copy()
    table["magnitude"] = table["contribution"].abs()
    shown = table.nlargest(10, "magnitude").sort_values("contribution")
    colors = np.where(shown["contribution"] >= 0, BLUE, RUST)
    with plt.rc_context({"font.family": ["Arial", "DejaVu Sans"], "axes.spines.top": False, "axes.spines.right": False}):
        figure, axis = plt.subplots(figsize=(8.5, 5.4), dpi=180)
        axis.barh(shown["predictor"], shown["contribution"], color=colors, height=0.64)
        axis.axvline(0, color="#6b7280", linewidth=0.8)
        axis.set_xlabel("Contribution to predicted CT-FFR")
        axis.set_title(
            f"Case {explanation.case_id}: local model explanation",
            loc="left",
            fontsize=13,
            fontweight="bold",
            pad=32,
        )
        axis.text(
            0,
            1.02,
            f"Base {explanation.base_value:.3f}  →  prediction {explanation.prediction:.3f}",
            transform=axis.transAxes,
            fontsize=9,
            color="#374151",
        )
        axis.grid(axis="x", color="#d1d5db", linewidth=0.5, alpha=0.7)
        figure.tight_layout()
    return figure


def contribution_figure(explanation: Explanation, path: Path) -> None:
    """Write one explanation as publication-resolution PNG and SVG files."""
    base = Path(path).with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)
    figure = contribution_plot(explanation)
    figure.savefig(base.with_suffix(".png"), dpi=300, bbox_inches="tight", facecolor="white")
    figure.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    plt.close(figure)
