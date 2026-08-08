"""Vendored preprocessing for the locked CT-FFR model.

Core helpers and feature logic are copied from
``src/crffr_hgb/data.py`` at research commit
``01618325b64fa0314a3da954c780943246992568``. Only canonical app input
column names replace the research workbook column names.
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

from .schema import MODEL_COLUMNS


def _numeric(value: Any) -> float:
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = str(value).strip().replace(",", "")
    match = re.search(r"[-+]?\d*\.?\d+", text)
    if not match:
        return np.nan
    number = float(match.group())
    if text.startswith("<"):
        return number / 2.0
    return number


def _binary(value: Any) -> float:
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value > 0)
    text = str(value).strip().upper()
    if text in {"1", "Y", "YES", "是", "有", "阳性", "+", "男", "M", "MALE", "TRUE"}:
        return 1.0
    if text in {"0", "N", "NO", "否", "无", "阴性", "-", "女", "F", "FEMALE", "FALSE"}:
        return 0.0
    return np.nan


def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    numerator = pd.to_numeric(numerator, errors="coerce")
    denominator = pd.to_numeric(denominator, errors="coerce")
    result = numerator / denominator
    return result.replace([np.inf, -np.inf], np.nan)


def _bmi_category(bmi: pd.Series) -> pd.Series:
    bmi = pd.to_numeric(bmi, errors="coerce")
    return pd.cut(
        bmi,
        bins=[-np.inf, 18.5, 24.0, 28.0, np.inf],
        labels=[0, 1, 2, 3],
        right=False,
    ).astype(float)


def _mifflin_bmr(weight: pd.Series, height: pd.Series, age: pd.Series, sex: pd.Series) -> pd.Series:
    weight = pd.to_numeric(weight, errors="coerce")
    height = pd.to_numeric(height, errors="coerce")
    age = pd.to_numeric(age, errors="coerce")
    sex = pd.to_numeric(sex, errors="coerce")
    base = 10.0 * weight + 6.25 * height - 5.0 * age
    return base + np.where(sex == 1, 5.0, -161.0)


def derive(raw: pd.DataFrame) -> pd.DataFrame:
    """Derive the ordered 23 model columns from canonical raw inputs.

    Args:
        raw: Canonically named input frame after schema validation.

    Returns:
        Numeric model input frame in the frozen metadata order.
    """
    output = pd.DataFrame(index=raw.index)
    sex = raw["sex"].map(_binary)
    age = raw["age"].map(_numeric)
    height = raw["height_cm"].map(_numeric)
    weight = raw["weight_kg"].map(_numeric)
    bmi = weight / np.square(height / 100.0)
    output["性别2"] = sex
    output["年龄字段"] = age
    output["是否高血压"] = raw["hypertension"].map(_binary)
    output["BMI分类"] = _bmi_category(bmi)
    output["基础代谢率BMR"] = _mifflin_bmr(weight, height, age, sex)
    output["是否吸烟"] = raw["smoking"].map(_binary)
    output["是否饮酒"] = raw["alcohol"].map(_binary)

    vessel = raw["target_vessel"].fillna("").astype(str).str.upper()
    output["Vessel_LAD"] = vessel.str.contains("LAD", regex=False).astype(int)
    output["Vessel_LCX"] = vessel.str.contains("LCX", regex=False).astype(int)
    output["Vessel_RCA"] = vessel.str.contains("RCA|RPDA", regex=True).astype(int)

    direct_map = {
        "血管斑块病变数": "plaque_lesions", "血管狭窄率": "diameter_stenosis",
        "斑块长度": "plaque_length", "最大面积狭窄率": "max_area_stenosis",
        "管腔最小截面积": "min_lumen_area", "斑块总负荷": "total_plaque_burden",
        "正性重构": "positive_remodeling", "低密度斑块": "low_attenuation_plaque",
        "餐巾指环": "napkin_ring_sign", "点状钙化": "spotty_calcification",
    }
    binary_targets = {"正性重构", "低密度斑块", "餐巾指环", "点状钙化"}
    for target, source in direct_map.items():
        output[target] = raw[source].map(_binary if target in binary_targets else _numeric)
    output["CP_ratio"] = _safe_ratio(raw["calcified_plaque_burden"], raw["total_plaque_burden"])
    output["LP_ratio"] = _safe_ratio(raw["lipid_plaque_burden"], raw["total_plaque_burden"])
    vulnerable = ["正性重构", "低密度斑块", "餐巾指环", "点状钙化"]
    output["易损斑块特征数"] = output[vulnerable].fillna(0).sum(axis=1)
    return output.loc[:, MODEL_COLUMNS]


def derived_summary(model_input: pd.DataFrame) -> pd.DataFrame:
    """Return six user-facing derived concepts for result downloads."""
    vessel = np.select(
        [model_input["Vessel_LAD"] == 1, model_input["Vessel_RCA"] == 1, model_input["Vessel_LCX"] == 1],
        ["LAD", "RCA", "LCX"],
        default="Unknown",
    )
    return pd.DataFrame(
        {
            "bmi_category": model_input["BMI分类"],
            "basal_metabolic_rate": model_input["基础代谢率BMR"],
            "vessel_indicator": vessel,
            "calcified_plaque_ratio": model_input["CP_ratio"],
            "lipid_plaque_ratio": model_input["LP_ratio"],
            "vulnerable_feature_count": model_input["易损斑块特征数"],
        },
        index=model_input.index,
    )

