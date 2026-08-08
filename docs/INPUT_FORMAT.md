# Input Format

Supply one row per lesion. The application accepts CSV, tab-separated text, XLSX, and legacy XLS files. Headers are trimmed and matched case-insensitively against canonical English names and documented Chinese aliases.

The contract contains one identifier (`case_id`) and 20 predictor-bearing raw fields. Users never calculate BMI category, basal metabolic rate, vessel indicators, plaque ratios, or vulnerable-feature count. The optional `reference_ctffr` field is retained only for an output error column.

Use `examples/sample_case.xlsx` or `examples/sample_batch.csv` as templates. Both are entirely synthetic. For every field, unit, range, and alias, see [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

## Validation behavior

- Missing columns, missing cells, unrecognized booleans or sex coding, invalid vessels, duplicate case IDs, impossible burdens, and values outside accepted bounds block prediction.
- Values within accepted bounds but outside the cohort-observed range produce an extrapolation warning.
- Errors always name the one-based row number and canonical field. A traceback is never a user-facing validation result.

Uploaded tables are held in memory and are not written by the application.

