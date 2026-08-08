"""Tests for the console interface over the shared API."""
import pandas as pd

from ctffr import predict, read_table
from ctffr.cli import main


def test_predict_writes_api_identical_file(tmp_path):
    output = tmp_path / "predictions.csv"
    assert main(["predict", "--input", "examples/sample_batch.csv", "--output", str(output)]) == 0
    expected = predict(read_table("examples/sample_batch.csv", "sample_batch.csv"))
    pd.testing.assert_frame_equal(pd.read_csv(output), expected, check_dtype=False)


def test_validate_returns_nonzero_and_names_bad_field(tmp_path, capsys, sample_raw):
    bad = tmp_path / "bad.csv"
    sample_raw.drop(columns=["min_lumen_area"]).to_csv(bad, index=False)
    assert main(["validate", "--input", str(bad)]) == 1
    assert "min_lumen_area" in capsys.readouterr().out


def test_explain_writes_figure_and_contributions(tmp_path):
    output = tmp_path / "explanation.png"
    assert main(["explain", "--input", "examples/sample_case.xlsx", "--case-id", "SYN-001", "--output", str(output)]) == 0
    assert output.exists()
    assert output.with_suffix(".svg").exists()
    assert output.with_name("explanation_contributions.csv").exists()

