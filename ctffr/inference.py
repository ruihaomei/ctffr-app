"""Integrity-checked shared inference implementation."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from .io import ValidationReport, canonicalize_headers, validate
from .preprocessing import derive, derived_summary
from .schema import FIELDS, MODEL_COLUMNS


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


class ValidationError(ValueError):
    """Raised when input validation blocks prediction."""


def format_report(report: ValidationReport) -> str:
    """Format a validation report as plain language."""
    lines = [
        f"{report.n_cases} case(s) detected.",
        f"{report.fields_found} of {report.fields_required} required fields found.",
    ]
    lines.extend(issue.message for issue in report.issues)
    return "\n".join(lines)


@lru_cache(maxsize=1)
def load_metadata() -> dict[str, Any]:
    """Load and validate frozen inference metadata."""
    metadata = json.loads((ARTIFACTS / "model_metadata.json").read_text(encoding="utf-8"))
    if metadata["feature_columns"] != list(MODEL_COLUMNS):
        raise RuntimeError("Model metadata feature columns do not match the application schema.")
    return metadata


@lru_cache(maxsize=1)
def load_model() -> Pipeline:
    """Load the model after verifying its SHA-256 integrity."""
    model_path = ARTIFACTS / "locked_model.joblib"
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if digest != load_metadata()["model_sha256"]:
        raise RuntimeError("The locked model file failed its integrity check.")
    model = joblib.load(model_path)
    if not isinstance(model, Pipeline):
        raise RuntimeError("The locked model artifact is not the expected pipeline.")
    return model


def predict(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate, derive, and score one or more lesions.

    Args:
        raw: Raw user input with canonical or recognized alias headers.

    Returns:
        Predictions, categories, raw inputs, and six derived concepts.

    Raises:
        ValidationError: If any blocking validation issue is found.
    """
    report = validate(raw)
    if report.blocking:
        raise ValidationError(format_report(report))
    canonical, _ = canonicalize_headers(raw)
    canonical = canonical.reset_index(drop=True)
    model_input = derive(canonical)
    predictions = load_model().predict(model_input)
    threshold = float(load_metadata()["reference_threshold"])
    result = pd.DataFrame(
        {
            "case_id": canonical["case_id"].astype(str),
            "predicted_ctffr": predictions,
            "threshold_category": [f"<= {threshold:.2f}" if value <= threshold else f"> {threshold:.2f}" for value in predictions],
        }
    )
    raw_columns = [field.name for field in FIELDS if field.name != "case_id"]
    result = pd.concat([result, canonical[raw_columns], derived_summary(model_input)], axis=1)
    if "reference_ctffr" in canonical:
        result["reference_ctffr"] = pd.to_numeric(canonical["reference_ctffr"], errors="coerce")
        result["error"] = result["predicted_ctffr"] - result["reference_ctffr"]
    return result


VERSION = str(load_metadata()["model_version"])
REFERENCE_THRESHOLD = float(load_metadata()["reference_threshold"])

