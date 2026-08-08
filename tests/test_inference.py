"""Tests for the shared inference API."""
import sys

import pandas as pd
import pytest

from ctffr import REFERENCE_THRESHOLD, ValidationError, predict
from ctffr import inference


def test_installed_wheel_artifact_location(tmp_path, monkeypatch):
    installed = tmp_path / "artifacts"
    installed.mkdir()
    monkeypatch.setattr(inference, "ROOT", tmp_path / "site-packages")
    monkeypatch.setattr(sys, "prefix", str(tmp_path))
    assert inference._resolve_artifacts() == installed


def test_chinese_and_english_headers_are_identical(sample_raw, chinese_headers):
    english = predict(sample_raw)
    chinese = predict(sample_raw.rename(columns=chinese_headers))
    pd.testing.assert_series_equal(english["predicted_ctffr"], chinese["predicted_ctffr"])


def test_threshold_and_optional_reference(sample_raw):
    sample_raw["reference_ctffr"] = 0.81
    out = predict(sample_raw)
    expected = "<= 0.80" if out.loc[0, "predicted_ctffr"] <= REFERENCE_THRESHOLD else "> 0.80"
    assert out.loc[0, "threshold_category"] == expected
    assert out.loc[0, "error"] == pytest.approx(out.loc[0, "predicted_ctffr"] - 0.81)


def test_blocking_validation_raises_readable_error(sample_raw):
    with pytest.raises(ValidationError, match="min_lumen_area") as excinfo:
        predict(sample_raw.drop(columns=["min_lumen_area"]))
    assert "Traceback" not in str(excinfo.value)
