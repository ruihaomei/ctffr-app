"""Single source of truth for CT-FFR input fields and model columns."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    """Describe one user-supplied input field."""

    name: str
    label: str
    unit: str
    dtype: str
    minimum: float | None
    maximum: float | None
    observed_min: float | None
    observed_max: float | None
    required: bool
    aliases: tuple[str, ...]
    tooltip: str


def _field(
    name: str,
    label: str,
    unit: str,
    dtype: str,
    minimum: float | None = None,
    maximum: float | None = None,
    *,
    observed: tuple[float, float] | None = None,
    aliases: tuple[str, ...] = (),
) -> Field:
    observed_min, observed_max = observed or (None, None)
    range_text = (
        f" Accepted range: {minimum:g} to {maximum:g} {unit}."
        if minimum is not None and maximum is not None
        else ""
    )
    return Field(
        name=name,
        label=label,
        unit=unit,
        dtype=dtype,
        minimum=minimum,
        maximum=maximum,
        observed_min=observed_min,
        observed_max=observed_max,
        required=True,
        aliases=aliases,
        tooltip=f"{label}.{range_text}".strip(),
    )


FIELDS: tuple[Field, ...] = (
    _field("case_id", "Study identifier for the case (do not enter a patient name)",
           "", "str", aliases=("姓名", "病例号")),
    _field("age", "Age", "years", "int", 18, 100, observed=(35, 95), aliases=("年龄",)),
    _field("sex", "Sex (male or female)", "", "enum", aliases=("性别",)),
    _field("height_cm", "Height", "cm", "float", 120, 220, aliases=("身高",)),
    _field("weight_kg", "Weight", "kg", "float", 30, 200, aliases=("体重",)),
    _field("hypertension", "History of hypertension (yes or no)", "", "bool", aliases=("高血压", "血压")),
    _field("smoking", "Smoking history (yes or no)", "", "bool", aliases=("吸烟",)),
    _field("alcohol", "Alcohol-use history (yes or no)", "", "bool", aliases=("饮酒", "喝酒")),
    _field("target_vessel", "Target vessel text containing LAD, LCX, RCA, or RPDA", "", "str", aliases=("斑块位置", "位置", "血管")),
    _field("plaque_lesions", "Number of plaque lesions", "count", "int", 0, 10, aliases=("斑块数", "血管斑块病变数")),
    _field("diameter_stenosis", "Diameter stenosis", "%", "float", 0, 100, observed=(31, 99), aliases=("狭窄率", "血管狭窄率")),
    _field("max_area_stenosis", "Maximum area stenosis", "%", "float", 0, 100, aliases=("最大面积狭窄率",)),
    _field("min_lumen_area", "Minimum lumen area", "mm²", "float", 0, 30, observed=(0, 26), aliases=("最小管腔面积", "管腔最小截面积")),
    _field("plaque_length", "Plaque length", "mm", "float", 0, 200, observed=(3.6, 121), aliases=("斑块长度", "长度")),
    _field("total_plaque_burden", "Total plaque burden", "%", "float", 0, 100, observed=(0, 85.8), aliases=("总斑块负荷", "斑块总负荷")),
    _field("calcified_plaque_burden", "Calcified plaque burden", "%", "float", 0, 100, aliases=("钙化斑块负荷",)),
    _field("lipid_plaque_burden", "Lipid plaque burden", "%", "float", 0, 100, aliases=("脂质斑块负荷",)),
    _field("positive_remodeling", "Positive remodeling (yes or no)", "", "bool", aliases=("正性重构",)),
    _field("low_attenuation_plaque", "Low-attenuation plaque (yes or no)", "", "bool", aliases=("低密度斑块", "低密度")),
    _field("napkin_ring_sign", "Napkin-ring sign (yes or no)", "", "bool", aliases=("餐巾环征", "餐巾指环")),
    _field("spotty_calcification", "Spotty calcification (yes or no)", "", "bool", aliases=("点状钙化",)),
)

MODEL_COLUMNS: tuple[str, ...] = (
    "性别2", "年龄字段", "是否高血压", "BMI分类", "基础代谢率BMR", "是否吸烟", "是否饮酒",
    "Vessel_LAD", "Vessel_RCA", "Vessel_LCX", "血管斑块病变数", "血管狭窄率", "斑块长度",
    "最大面积狭窄率", "管腔最小截面积", "斑块总负荷", "CP_ratio", "LP_ratio", "易损斑块特征数",
    "正性重构", "低密度斑块", "餐巾指环", "点状钙化",
)


def field_by_name(name: str) -> Field:
    """Return a field by canonical name.

    Raises:
        KeyError: If ``name`` is not in the input contract.
    """
    for field in FIELDS:
        if field.name == name:
            return field
    raise KeyError(name)


def match_header(header: str) -> Field | None:
    """Match a trimmed, case-insensitive canonical name or alias."""
    candidate = str(header).strip().casefold().replace("_", " ")
    for field in FIELDS:
        options = (field.name, field.name.replace("_", " "), field.label, *field.aliases)
        if candidate in {option.strip().casefold().replace("_", " ") for option in options}:
            return field
    return None

