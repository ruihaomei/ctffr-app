"""Render the input data dictionary from the executable schema."""
from __future__ import annotations

from pathlib import Path

from ctffr.schema import FIELDS


def render() -> str:
    """Return deterministic Markdown for every input field."""
    lines = [
        "# Data Dictionary",
        "",
        "This file is generated from `ctffr/schema.py`; do not edit it manually.",
        "",
        "| Field | Definition | Unit | Type | Accepted values | Chinese aliases |",
        "|---|---|---:|---|---|---|",
    ]
    for field in FIELDS:
        accepted = (
            f"{field.minimum:g} to {field.maximum:g}"
            if field.minimum is not None
            else {"bool": "yes/no", "enum": "male/female", "str": "non-empty text"}[field.dtype]
        )
        aliases = ", ".join(field.aliases) or "—"
        lines.append(
            f"| `{field.name}` | {field.label} | {field.unit or '—'} | {field.dtype} | {accepted} | {aliases} |"
        )
    lines.extend(
        [
            "",
            "Values inside an accepted range but outside a cohort-observed range produce a warning, not an error.",
            "The optional `reference_ctffr` column is used only to calculate prediction error and is never supplied to the model.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    """Write the generated data dictionary under `docs/`."""
    root = Path(__file__).resolve().parents[1]
    (root / "docs" / "DATA_DICTIONARY.md").write_text(render(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

