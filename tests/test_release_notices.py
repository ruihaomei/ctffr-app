"""Release metadata and public-disclosure checks."""
from pathlib import Path


def test_mit_license_and_metadata_agree():
    license_text = Path("LICENSE").read_text(encoding="utf-8")
    metadata = Path("pyproject.toml").read_text(encoding="utf-8")
    assert license_text.startswith("MIT License")
    assert "Copyright (c) 2026" in license_text
    assert 'license = {text = "MIT"}' in metadata


def test_readme_discloses_scope_and_centroid_shap_difference():
    readme = Path("README.md").read_text(encoding="utf-8")
    for phrase in (
        "For academic research use only",
        "Not for clinical diagnosis or decision-making",
        "25 k-means cluster centroids",
        "-0.00635",
        "case-level contribution differences",
    ):
        assert phrase in readme


def test_model_documentation_reports_locked_external_metrics():
    model_doc = Path("docs/MODEL.md").read_text(encoding="utf-8")
    assert "external MAE 0.064 and RMSE 0.081" in model_doc
