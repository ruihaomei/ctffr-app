"""Streamlit smoke and architecture tests."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_starts_and_tutorial_is_visible():
    app = AppTest.from_file("app/streamlit_app.py").run(timeout=20)
    assert not app.exception
    assert any("Getting started" in item.value for item in app.markdown)


def test_ui_module_contains_no_model_logic():
    source = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    for forbidden in ("joblib", "sklearn", "shap.", "0.80", "predict_proba"):
        assert forbidden not in source
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert imports == ["import ctffr", "import streamlit as st"]


def test_academic_and_nonclinical_notice_is_visible():
    app = AppTest.from_file("app/streamlit_app.py").run(timeout=20)
    notices = [item.value for item in app.markdown]
    assert any("academic research use only" in value for value in notices)
    assert any("Not for clinical diagnosis or decision-making" in value for value in notices)
