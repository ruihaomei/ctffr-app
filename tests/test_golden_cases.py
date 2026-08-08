"""The non-negotiable model regression gate."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from ctffr import load_metadata, predict
from ctffr.schema import MODEL_COLUMNS


def test_every_golden_case_reproduces():
    golden = json.loads(Path("artifacts/golden_cases.json").read_text(encoding="utf-8"))
    got = predict(pd.DataFrame([case["input"] for case in golden["cases"]]))
    for case, value in zip(golden["cases"], got["predicted_ctffr"], strict=True):
        assert value == pytest.approx(case["expected_predicted_ctffr"], abs=1e-9)


def test_model_and_schema_integrity():
    digest = hashlib.sha256(Path("artifacts/locked_model.joblib").read_bytes()).hexdigest()
    metadata = load_metadata()
    assert digest == metadata["model_sha256"]
    assert list(MODEL_COLUMNS) == metadata["feature_columns"]

