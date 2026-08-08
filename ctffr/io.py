"""Input reading, alias normalization, validation, and result writing."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

import pandas as pd

from .schema import FIELDS, Field, match_header


@dataclass(frozen=True)
class Issue:
    """One plain-language validation issue."""

    severity: str
    row: int | None
    field: str | None
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """Aggregate input validation outcome."""

    n_cases: int
    fields_found: int
    fields_required: int
    issues: tuple[Issue, ...]

    @property
    def blocking(self) -> bool:
        """Return whether any error blocks prediction."""
        return any(issue.severity == "error" for issue in self.issues)


def canonicalize_headers(raw: pd.DataFrame) -> tuple[pd.DataFrame, tuple[Issue, ...]]:
    """Rename recognized English or Chinese headers to canonical names."""
    renamed: dict[Any, str] = {}
    matches: dict[str, list[str]] = {}
    for column in raw.columns:
        field = match_header(str(column))
        if field:
            renamed[column] = field.name
            matches.setdefault(field.name, []).append(str(column))
        elif str(column).strip().casefold() == "reference_ctffr":
            renamed[column] = "reference_ctffr"
    issues = tuple(
        Issue("error", None, name, f"Field '{name}' appears more than once: {', '.join(headers)}.")
        for name, headers in matches.items()
        if len(headers) > 1
    )
    return raw.rename(columns=renamed).copy(), issues


def read_table(path_or_buffer: str | Path | IO[bytes], filename: str) -> pd.DataFrame:
    """Read CSV, TSV, XLSX, or XLS data without writing it to disk."""
    suffix = Path(filename).suffix.casefold()
    if suffix == ".csv":
        return pd.read_csv(path_or_buffer)
    if suffix == ".tsv":
        return pd.read_csv(path_or_buffer, sep="\t")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path_or_buffer)
    raise ValueError("Unsupported file type. Use CSV, TSV, XLSX, or XLS.")


def _invalid_type(field: Field, value: Any) -> bool:
    if pd.isna(value) or str(value).strip() == "":
        return False
    if field.dtype in {"int", "float"}:
        number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        return pd.isna(number) or (field.dtype == "int" and float(number) % 1 != 0)
    normalized = str(value).strip().casefold()
    if field.dtype == "bool":
        return normalized not in {"1", "0", "y", "n", "yes", "no", "true", "false", "是", "否", "有", "无"}
    if field.dtype == "enum":
        return normalized not in {"1", "0", "m", "f", "male", "female", "男", "女"}
    return False


def validate(raw: pd.DataFrame) -> ValidationReport:
    """Validate aliases, required values, types, ranges, and cross-field rules."""
    canonical, header_issues = canonicalize_headers(raw)
    issues = list(header_issues)
    found = sum(field.name in canonical for field in FIELDS)
    for field in FIELDS:
        if field.name not in canonical:
            issues.append(Issue("error", None, field.name, f"Required field '{field.name}' was not found."))
            continue
        for position, value in enumerate(canonical[field.name], 1):
            if pd.isna(value) or str(value).strip() == "":
                issues.append(Issue("error", position, field.name, f"Row {position}: field '{field.name}' is missing."))
                continue
            if _invalid_type(field, value):
                issues.append(Issue("error", position, field.name, f"Row {position}: field '{field.name}' has an unrecognized value."))
                continue
            if field.dtype in {"int", "float"}:
                number = float(value)
                if number < float(field.minimum) or number > float(field.maximum):
                    issues.append(Issue("error", position, field.name, f"Row {position}: field '{field.name}' must be between {field.minimum:g} and {field.maximum:g}."))
                elif field.observed_min is not None and not field.observed_min <= number <= field.observed_max:
                    issues.append(Issue("warning", position, field.name, f"Row {position}: field '{field.name}' is outside the model's observed range ({field.observed_min:g} to {field.observed_max:g}); this is extrapolation."))

    if "case_id" in canonical:
        duplicates = canonical["case_id"].astype(str).str.strip().duplicated(keep=False)
        for position in canonical.index[duplicates]:
            row = canonical.index.get_loc(position) + 1
            issues.append(Issue("error", row, "case_id", f"Row {row}: field 'case_id' must be unique."))
    if "target_vessel" in canonical:
        for position, value in enumerate(canonical["target_vessel"], 1):
            text = str(value).upper()
            matched = sum(("LAD" in text, "LCX" in text, "RCA" in text or "RPDA" in text))
            if matched != 1:
                issues.append(Issue("error", position, "target_vessel", f"Row {position}: field 'target_vessel' must identify exactly one of LAD, LCX, RCA, or RPDA."))
    burden_columns = {"total_plaque_burden", "calcified_plaque_burden", "lipid_plaque_burden"}
    if burden_columns.issubset(canonical.columns):
        total = pd.to_numeric(canonical["total_plaque_burden"], errors="coerce")
        for name in ("calcified_plaque_burden", "lipid_plaque_burden"):
            component = pd.to_numeric(canonical[name], errors="coerce")
            for position in canonical.index[component > total]:
                row = canonical.index.get_loc(position) + 1
                issues.append(Issue("error", row, name, f"Row {row}: field '{name}' cannot exceed 'total_plaque_burden'."))
    return ValidationReport(len(canonical), found, len(FIELDS), tuple(issues))


def write_results(frame: pd.DataFrame, path: Path) -> None:
    """Write results as CSV or XLSX according to the destination suffix."""
    path = Path(path)
    if path.suffix.casefold() == ".csv":
        frame.to_csv(path, index=False)
    elif path.suffix.casefold() == ".xlsx":
        frame.to_excel(path, index=False)
    else:
        raise ValueError("Unsupported output type. Use CSV or XLSX.")

