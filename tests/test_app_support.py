"""Tests for UI-safe byte and table adapters."""
import pandas as pd
import pytest

from ctffr import (
    explain,
    field_table,
    figure_bytes,
    frame_from_records,
    prediction_bytes,
    results_table_html,
    sample_case,
    sample_file_bytes,
    threshold_statement,
)


def test_ui_helpers_are_schema_and_sample_backed():
    case = sample_case()
    assert case["case_id"] == "SYN-001"
    assert len(field_table()) == 21
    assert "0.80" in threshold_statement()
    assert sample_file_bytes()[:2] == b"PK"
    assert len(frame_from_records([case])) == 1


def test_prediction_download_bytes(sample_raw):
    csv_bytes = prediction_bytes(sample_raw, "csv")
    xlsx_bytes = prediction_bytes(sample_raw, "xlsx")
    assert b"case_id" in csv_bytes
    assert xlsx_bytes[:2] == b"PK"
    assert len(pd.read_csv(pd.io.common.BytesIO(csv_bytes))) == 1
    with pytest.raises(ValueError, match="Download type"):
        prediction_bytes(sample_raw, "pdf")


def test_explanation_download_bytes(sample_raw):
    explanation = explain(sample_raw, "SYN-001")
    assert figure_bytes(explanation, "png")[:8] == b"\x89PNG\r\n\x1a\n"
    assert b"<svg" in figure_bytes(explanation, "svg")
    with pytest.raises(ValueError, match="Figure type"):
        figure_bytes(explanation, "pdf")


def test_batch_table_uses_three_line_markup():
    frame = pd.DataFrame({"case_id": ["A"], "predicted_ctffr": [0.81234], "threshold_category": ["> 0.80"]})
    html = results_table_html(frame)
    assert "results-table" in html and "0.8123" in html
    assert "border=\"" not in html
