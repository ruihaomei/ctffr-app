"""Synthetic fixtures shared by the standalone application tests."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_raw() -> pd.DataFrame:
    """Return the first hand-authored golden lesion as a one-row frame."""
    golden = json.loads(Path("artifacts/golden_cases.json").read_text(encoding="utf-8"))
    return pd.DataFrame([golden["cases"][0]["input"]])


@pytest.fixture
def chinese_headers() -> dict[str, str]:
    """Return one unambiguous Chinese alias for every canonical input header."""
    return {
        "case_id": "病例号", "age": "年龄", "sex": "性别", "height_cm": "身高",
        "weight_kg": "体重", "hypertension": "高血压", "smoking": "吸烟",
        "alcohol": "饮酒", "target_vessel": "斑块位置", "plaque_lesions": "斑块数",
        "diameter_stenosis": "狭窄率", "max_area_stenosis": "最大面积狭窄率",
        "min_lumen_area": "最小管腔面积", "plaque_length": "斑块长度",
        "total_plaque_burden": "总斑块负荷", "calcified_plaque_burden": "钙化斑块负荷",
        "lipid_plaque_burden": "脂质斑块负荷", "positive_remodeling": "正性重构",
        "low_attenuation_plaque": "低密度斑块", "napkin_ring_sign": "餐巾环征",
        "spotty_calcification": "点状钙化",
    }

