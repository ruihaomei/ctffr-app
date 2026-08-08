# Implementation Notes

## Delivered

- One integrity-checked inference implementation shared by Python, CLI, and Streamlit.
- Alias-aware schema validation and verbatim-vendored research derivations.
- Local SHAP using 25 aggregate centroids, with PNG/SVG/CSV downloads.
- Ten synthetic golden cases, sample files, generated data dictionary, Docker packaging, and automated tests.

## Necessary deviation from the brief

The first exported sklearn pipeline retained a pickle reference to the research-only function `crffr_hgb.search._dense`, so it could not load in a clean standalone environment. The exporter now makes the already-fitted `ColumnTransformer` emit dense output and converts the custom function transformer to sklearn's built-in identity transform. Golden predictions remain identical to `1e-9`, and serialization round-trip remains exact.

## Owner review required

- Select and insert the final software licence. `LICENSE` is intentionally not a grant of rights.
- Replace all `CITATION.cff` placeholders with the complete author list, ORCIDs, repository URL, manuscript citation, journal, year, and DOI.
- Confirm acceptance of centroid-background SHAP and its documented small difference from manuscript SHAP.

## Verification limits

The final clean Python 3.12 environment passed 34 tests at 92.10% branch-aware coverage. CLI validate/predict/explain, wheel build and wheel installation, golden prediction parity, model integrity, generated-document freshness, privacy scans, and real-browser single/batch workflows all passed. Docker could not be built locally because the host has no Docker executable; the Dockerfile is included, but container execution remains the only unverified gate. No hosted deployment or external-network workflow was introduced.
