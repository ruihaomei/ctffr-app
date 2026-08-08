"""Generate public example files exclusively from committed synthetic golden cases."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ctffr import predict


def generate(root: Path) -> None:
    """Regenerate the sample inputs and expected output."""
    golden = json.loads((root / "artifacts" / "golden_cases.json").read_text(encoding="utf-8"))
    raw = pd.DataFrame([case["input"] for case in golden["cases"]])
    examples = root / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    raw.iloc[[0]].to_excel(examples / "sample_case.xlsx", index=False)
    raw.to_csv(examples / "sample_batch.csv", index=False)
    predict(raw).to_csv(examples / "expected_output.csv", index=False)


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1])
