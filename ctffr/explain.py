"""Centroid-background SHAP explanations for individual lesions."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import shap

from .inference import ARTIFACTS, ValidationError, format_report, load_model
from .io import canonicalize_headers, validate
from .preprocessing import derive
from .schema import MODEL_COLUMNS


DISPLAY_LABELS = {
    "性别2": "Sex", "年龄字段": "Age", "是否高血压": "Hypertension", "BMI分类": "BMI category",
    "基础代谢率BMR": "Basal metabolic rate", "是否吸烟": "Smoking", "是否饮酒": "Alcohol use",
    "Vessel_LAD": "LAD location", "Vessel_RCA": "RCA location", "Vessel_LCX": "LCX location",
    "血管斑块病变数": "Number of plaque lesions", "血管狭窄率": "Diameter stenosis",
    "斑块长度": "Plaque length", "最大面积狭窄率": "Maximum area stenosis",
    "管腔最小截面积": "Minimum lumen area", "斑块总负荷": "Total plaque burden",
    "CP_ratio": "Calcified plaque ratio", "LP_ratio": "Lipid plaque ratio",
    "易损斑块特征数": "Vulnerable feature count", "正性重构": "Positive remodeling",
    "低密度斑块": "Low-attenuation plaque", "餐巾指环": "Napkin-ring sign", "点状钙化": "Spotty calcification",
}


@dataclass(frozen=True)
class Explanation:
    """One local additive explanation in predicted CT-FFR units."""

    case_id: str
    base_value: float
    prediction: float
    contributions: pd.DataFrame
    additivity_residual: float


def _background() -> pd.DataFrame:
    """Load the aggregate 25-centroid background and verify its feature order."""
    archive = np.load(ARTIFACTS / "shap_background.npz")
    columns = [str(value) for value in archive["feature_columns"]]
    if columns != list(MODEL_COLUMNS):
        raise RuntimeError("SHAP background columns do not match the model schema.")
    return pd.DataFrame(archive["data"], columns=columns)


def explain(raw: pd.DataFrame, case_id: str) -> Explanation:
    """Explain one case using a privacy-safe centroid background.

    Args:
        raw: One or more raw input lesions.
        case_id: Identifier of the lesion to explain.

    Returns:
        Additive SHAP contributions for all 23 model columns.

    Raises:
        ValidationError: If input validation blocks inference.
        KeyError: If ``case_id`` is not present or is not unique.
    """
    report = validate(raw)
    if report.blocking:
        raise ValidationError(format_report(report))
    canonical, _ = canonicalize_headers(raw)
    positions = canonical.index[canonical["case_id"].astype(str) == str(case_id)].tolist()
    if len(positions) != 1:
        raise KeyError(f"Case ID '{case_id}' was not found exactly once.")
    model_input = derive(canonical.loc[[positions[0]]]).reset_index(drop=True)
    model = load_model()
    background = _background()

    def prediction_function(values: np.ndarray | pd.DataFrame) -> np.ndarray:
        frame = pd.DataFrame(values, columns=MODEL_COLUMNS)
        return np.asarray(model.predict(frame), dtype=float)

    explainer = shap.Explainer(prediction_function, background, algorithm="permutation")
    shap_result = explainer(model_input, max_evals=2 * len(MODEL_COLUMNS) + 1)
    contributions = np.asarray(shap_result.values[0], dtype=float)
    base_value = float(np.asarray(shap_result.base_values).reshape(-1)[0])
    prediction = float(model.predict(model_input)[0])
    table = pd.DataFrame(
        {
            "predictor": [DISPLAY_LABELS[column] for column in MODEL_COLUMNS],
            "model_column": MODEL_COLUMNS,
            "value": model_input.iloc[0].to_numpy(dtype=float),
            "display": [f"{value:.4g}" for value in model_input.iloc[0].to_numpy(dtype=float)],
            "contribution": contributions,
        }
    )
    residual = prediction - (base_value + float(contributions.sum()))
    return Explanation(str(case_id), base_value, prediction, table, residual)

