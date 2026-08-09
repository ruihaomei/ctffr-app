"""Small presentation adapters that keep Streamlit free of data/model logic."""
from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from .explain import Explanation
from .inference import ARTIFACTS, REFERENCE_THRESHOLD
from .plotting import contribution_plot
from .schema import FIELDS


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_USE_STATEMENT = (
    "**For academic research use only. Not for clinical diagnosis or decision-making.** "
    "This software is not a medical device, has not been prospectively validated for clinical "
    "deployment, and must not be used to direct patient care."
)
CTFFR_STATEMENT = (
    "The model estimates CT-derived fractional flow reserve. CT-FFR is itself a computational "
    "estimate of invasive fractional flow reserve; this software does not predict invasive FFR."
)


def sample_case() -> dict[str, Any]:
    """Return the first committed synthetic golden input."""
    golden = json.loads((ARTIFACTS / "golden_cases.json").read_text(encoding="utf-8"))
    return dict(golden["cases"][0]["input"])


def sample_file_bytes() -> bytes:
    """Return the one-case synthetic XLSX sample."""
    return (ROOT / "examples" / "sample_case.xlsx").read_bytes()


def frame_from_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Build an in-memory input frame for the web form."""
    return pd.DataFrame.from_records(records)


def field_table() -> pd.DataFrame:
    """Return the schema as a user-facing data dictionary table."""
    return pd.DataFrame(
        [
            {
                "Field": field.name,
                "Definition": field.label,
                "Unit": field.unit or "—",
                "Accepted range / coding": (
                    f"{field.minimum:g}–{field.maximum:g}"
                    if field.minimum is not None
                    else field.dtype
                ),
            }
            for field in FIELDS
        ]
    )


def threshold_statement() -> str:
    """Return the reporting-threshold interpretation from frozen metadata."""
    return f"A predicted CT-FFR ≤ {REFERENCE_THRESHOLD:.2f} is reported as below the reference threshold for abnormal physiology."


def prediction_bytes(frame: pd.DataFrame, kind: str) -> bytes:
    """Serialize an in-memory result frame for browser download."""
    buffer = io.BytesIO()
    if kind == "csv":
        return frame.to_csv(index=False).encode("utf-8")
    if kind == "xlsx":
        frame.to_excel(buffer, index=False)
        return buffer.getvalue()
    raise ValueError("Download type must be 'csv' or 'xlsx'.")


def results_table_html(frame: pd.DataFrame) -> str:
    """Render batch predictions as a scrollable three-line table."""
    display = frame[["case_id", "predicted_ctffr", "threshold_category"]].copy()
    display["predicted_ctffr"] = display["predicted_ctffr"].map(lambda value: f"{value:.4f}")
    return f'<div class="results-scroll">{display.to_html(index=False, border=0, classes="results-table")}</div>'


def figure_bytes(explanation: Explanation, kind: str) -> bytes:
    """Render one contribution figure to in-memory PNG or SVG bytes."""
    if kind not in {"png", "svg"}:
        raise ValueError("Figure type must be 'png' or 'svg'.")
    buffer = io.BytesIO()
    figure = contribution_plot(explanation)
    figure.savefig(buffer, format=kind, dpi=300 if kind == "png" else None, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return buffer.getvalue()
