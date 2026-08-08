"""Tests for centroid-background SHAP and its figure."""
import pytest

from ctffr.explain import explain
from ctffr.plotting import contribution_figure


def test_shap_additivity_and_shape(sample_raw):
    result = explain(sample_raw, case_id="SYN-001")
    assert result.base_value + result.contributions["contribution"].sum() == pytest.approx(result.prediction, abs=1e-6)
    assert len(result.contributions) == 23
    assert abs(result.additivity_residual) < 1e-6


def test_unknown_case_is_readable(sample_raw):
    with pytest.raises(KeyError, match="NOPE"):
        explain(sample_raw, case_id="NOPE")


def test_figure_writes_png_and_svg(tmp_path, sample_raw):
    contribution_figure(explain(sample_raw, "SYN-001"), tmp_path / "explanation")
    assert (tmp_path / "explanation.png").exists()
    assert (tmp_path / "explanation.svg").exists()

