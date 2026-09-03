"""Freshness and privacy tests for generated public files."""
from pathlib import Path

import pandas as pd

from ctffr import predict, read_table
from scripts.generate_data_dictionary import render


def test_data_dictionary_is_fresh():
    assert Path("docs/DATA_DICTIONARY.md").read_text(encoding="utf-8") == render()


def test_expected_output_is_fresh():
    expected = pd.read_csv("examples/expected_output.csv")
    actual = predict(read_table("examples/sample_batch.csv", "sample_batch.csv"))
    pd.testing.assert_frame_equal(expected, actual, check_dtype=False, atol=1e-12)


#: Directories that are not part of the source tree. A reader who follows the
#: README makes a virtual environment right here, and the packages it installs
#: ship their own CSV fixtures; without this the privacy check fails for them and
#: reads as though the repository were leaking tables.
NOT_SOURCE = {"build", "dist", "node_modules", "htmlcov", "site-packages"}


def _source_files():
    for path in Path(".").rglob("*"):
        parts = path.parts
        if any(part.startswith(".") or part in NOT_SOURCE for part in parts):
            continue
        yield path


def test_public_tables_exist_only_under_examples():
    tables = [path for path in _source_files()
              if path.suffix.casefold() in {".csv", ".xlsx", ".xls"}]
    assert tables
    assert all(path.parts[0] == "examples" for path in tables)

