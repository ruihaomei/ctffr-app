"""Tests for table reading, validation, and result writing."""
from __future__ import annotations

import io

import pandas as pd
import pytest

from ctffr.io import read_table, validate, write_results


def test_missing_field_and_bad_value_errors_are_readable(sample_raw):
    report = validate(sample_raw.drop(columns=["min_lumen_area"]))
    assert report.blocking
    assert any("min_lumen_area" in issue.message for issue in report.issues)
    sample_raw.loc[0, "diameter_stenosis"] = 150
    issue = next(i for i in validate(sample_raw).issues if i.field == "diameter_stenosis")
    assert issue.severity == "error" and issue.row == 1


def test_warning_does_not_block_and_constraints_do(sample_raw):
    sample_raw.loc[0, "age"] = 25
    report = validate(sample_raw)
    assert not report.blocking and any(i.severity == "warning" for i in report.issues)
    sample_raw.loc[0, "calcified_plaque_burden"] = 90
    assert validate(sample_raw).blocking
    sample_raw.loc[0, "calcified_plaque_burden"] = 8
    sample_raw.loc[0, "target_vessel"] = "left main"
    assert validate(sample_raw).blocking


def test_duplicates_types_missing_values_and_jargon(sample_raw):
    assert validate(pd.concat([sample_raw, sample_raw], ignore_index=True)).blocking
    sample_raw.loc[0, "age"] = "old"
    sample_raw.loc[0, "smoking"] = "maybe"
    sample_raw.loc[0, "plaque_length"] = None
    report = validate(sample_raw)
    assert report.blocking
    for issue in report.issues:
        assert not any(word in issue.message for word in ("Traceback", "KeyError", "dtype", "NaN"))


@pytest.mark.parametrize("filename", ["cases.csv", "cases.tsv", "cases.xlsx"])
def test_read_and_write_supported_formats(tmp_path, sample_raw, filename):
    path = tmp_path / filename
    if path.suffix == ".csv":
        sample_raw.to_csv(path, index=False)
    elif path.suffix == ".tsv":
        sample_raw.to_csv(path, sep="\t", index=False)
    else:
        sample_raw.to_excel(path, index=False)
    got = read_table(path, filename)
    assert len(got) == 1
    output = tmp_path / ("out.xlsx" if path.suffix == ".csv" else "out.csv")
    write_results(got, output)
    assert output.exists()


def test_read_buffer_and_reject_unsupported(sample_raw):
    buffer = io.BytesIO(sample_raw.to_csv(index=False).encode())
    assert len(read_table(buffer, "cases.csv")) == 1
    with pytest.raises(ValueError, match="Unsupported"):
        read_table(buffer, "cases.json")

