"""Tests for the single-source input schema."""
from ctffr.schema import FIELDS, field_by_name, match_header


def test_twenty_predictor_fields():
    assert len([field for field in FIELDS if field.name != "case_id"]) == 20


def test_chinese_and_trimmed_headers_match():
    assert match_header("最小管腔面积").name == "min_lumen_area"
    assert match_header("  Diameter Stenosis ").name == "diameter_stenosis"
    assert match_header("unknown") is None


def test_field_lookup_and_descriptions_are_complete():
    assert field_by_name("age").minimum == 18
    for field in FIELDS:
        assert field.tooltip
        assert field.unit or field.dtype in {"bool", "enum", "str"}

