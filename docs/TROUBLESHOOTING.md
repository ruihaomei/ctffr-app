# Troubleshooting

## The application will not start

Confirm that Python 3.12 is active, then run `pip install -e .`. If the locked model fails its integrity check, restore the original `artifacts/locked_model.joblib`; do not bypass the hash check.

## A file is rejected

- **Required field was not found:** rename the column to its canonical name or a documented alias.
- **Field is missing:** fill the named cell on the reported row.
- **Unrecognized value:** use the coding in the data dictionary; booleans accept yes/no, Y/N, true/false, 1/0, or the documented Chinese equivalents.
- **Value must be between bounds:** correct the measurement or unit.
- **Target vessel:** include exactly one of LAD, LCX, RCA, or RPDA.
- **Plaque component exceeds total burden:** correct the component or total plaque burden.
- **Case ID must be unique:** assign a unique non-empty identifier to every lesion row.

Warnings about the observed range do not block prediction. They mean the valid input lies outside the study cohorts' observed span and the result is an extrapolation.

## A SHAP chart differs from the manuscript

This is expected because the public app uses aggregate k-means centroids instead of private patient rows. See [MODEL.md](MODEL.md) for the fixed base-value difference and the limits of case-level comparisons.

## Docker cannot bind the port

Another process may be using port 8501. Stop it or map a different host port, for example `docker run --rm -p 8502:8501 ctffr`.
