"""Regression tests for the vendored research preprocessing."""
import pytest

from ctffr.preprocessing import derive


def test_hand_computed_derivations(sample_raw):
    out = derive(sample_raw)
    assert out["BMI分类"].iloc[0] == 2
    assert out["基础代谢率BMR"].iloc[0] == pytest.approx(1477.5)
    assert out["CP_ratio"].iloc[0] == pytest.approx(0.40)
    assert out["LP_ratio"].iloc[0] == pytest.approx(0.025)
    assert out["易损斑块特征数"].iloc[0] == 2
    assert tuple(out.loc[0, ["Vessel_LAD", "Vessel_LCX", "Vessel_RCA"]]) == (1, 0, 0)
    assert out.isna().sum().sum() == 0


def test_rpda_counts_as_rca(sample_raw):
    sample_raw.loc[0, "target_vessel"] = "RPDA"
    assert derive(sample_raw)["Vessel_RCA"].iloc[0] == 1


def test_zero_total_burden_does_not_raise(sample_raw):
    sample_raw.loc[0, ["total_plaque_burden", "calcified_plaque_burden", "lipid_plaque_burden"]] = 0
    out = derive(sample_raw)
    assert out.loc[0, "CP_ratio"] != float("inf")
    assert out.loc[0, "LP_ratio"] != float("inf")
