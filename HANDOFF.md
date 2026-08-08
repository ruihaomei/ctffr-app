# CT-FFR App — Current Handoff

Current through 2026-08-08 (Asia/Shanghai). Read this file before modifying the standalone application, artifacts, screenshots, or release documentation.

## Restart in 60 seconds

Repository: `release/ctffr-app`

Branch: `codex/ctffr-app`

Run the verification suite:

```bash
pytest
```

Expected result: `34 passed`. The last clean Python 3.12 coverage run reported 92.10% branch-aware coverage. Docker execution remains unverified because Docker is not installed on the current host.

Start the app after installing the package:

```bash
pip install -e .
streamlit run app/streamlit_app.py
```

## Delivered surface

- One locked inference implementation shared by the Python API, CLI, and Streamlit.
- Manual single-case and CSV/TSV/XLSX/XLS batch workflows.
- Alias-aware validation, research-derived feature engineering, continuous CT-FFR output, and the prespecified `0.80` reporting category.
- Local SHAP explanations and CSV/XLSX/PNG/SVG exports.
- Ten synthetic golden cases, synthetic examples, generated data dictionary, Dockerfile, and automated tests.
- Screenshot-led English [guided demo](docs/DEMO.md), linked from [README](README.md) and [quick start](docs/QUICKSTART.md).

## Non-negotiable constraints

1. Do not refit, retune, reselect, or replace the locked model.
2. Do not publish patient rows, private predictions, or real-patient examples.
3. Keep Web, CLI, and Python API on the same package-level inference path.
4. Keep `CTFFR <= 0.80` as a reporting convention, not a diagnosis.
5. State that the software estimates CT-FFR, not invasive FFR, and is for research use only.
6. Do not replace the 25-centroid SHAP background with the private 64-row background.
7. Do not invent LICENSE or citation metadata.

## Locked artifacts and numerical gates

| Artifact or gate | Current state |
|---|---|
| `artifacts/locked_model.joblib` | Integrity checked at load time |
| Model SHA-256 | `d61e14e320a76d6d8d32ecc4e1ff10694286bd89ba296f10ecc790f0069627d4` |
| `artifacts/golden_cases.json` | 10 synthetic cases; prediction parity required |
| `artifacts/shap_background.npz` | 25 aggregate k-means centroids; no patient rows |
| SHAP additivity | Baseline plus 23 contributions reconstructs prediction within `1e-6` |
| Tests | 34 passing |
| Last coverage result | 92.10% branch-aware |

The fitted pipeline was made standalone by forcing the already-fitted `ColumnTransformer` to emit dense output and replacing the research-only `_dense` function reference with sklearn's identity transform. Golden predictions remained identical within `1e-9`; do not undo this portability fix.

## SHAP privacy decision awaiting professor approval

The manuscript analysis uses 64 private development-cohort rows as its SHAP background. The app distributes 25 aggregate centroids instead.

| Quantity | Private 64 rows | App centroids | Difference |
|---|---:|---:|---:|
| Baseline | 0.75341 | 0.74707 | -0.00634 |
| Largest single contribution change | — | — | 0.0086 |
| Top-five features | Same set | Same set | Ranks 2 and 3 swap |

Recommended decision: accept the small quantified difference and retain the disclosure in `docs/MODEL.md`. Publishing the private patient rows is not an acceptable alternative.

## Owner decisions still open

- `LICENSE` intentionally remains `LICENCE TBD`. The current recommendation is Apache 2.0 for its explicit patent terms; MIT remains the simpler permissive option.
- `CITATION.cff` still needs the final author order, standardized English names, ORCIDs, repository URL, manuscript title, journal, year, and DOI.
- Professor approval is required for the centroid-background SHAP release posture.
- Build and run the Docker image on a host with Docker before public release.

Do not publish the repository until these gates are closed.

## Documentation and screenshot reuse

The canonical English screenshots are:

- `docs/images/single_case.png`
- `docs/images/batch.png`

They are reused by `README.md`, `docs/DEMO.md`, and the Chinese professor-review Word document in the adjacent research package. If UI changes materially, recapture both at the same dimensions, update all consumers, and rerun the visual and privacy checks.

The Chinese review materials live outside this repository at:

```text
release/cta_ha_external_hgb_primary_CANONICAL_20260627/docs/ctffr-app/
```

Key files there are `CT-FFR_Demo_教授审核版_20260808.docx`, `PROFESSOR_EMAIL_ZH.md`, `PRD.md`, and `CODEX_PROMPT.md`.

## Suggested next work

1. Obtain the professor's three decisions and fill LICENSE/CITATION only from confirmed information.
2. Run Docker build/start/health checks on a Docker-enabled host.
3. After any UI change, run `pytest`, verify generated-file freshness, exercise single and batch workflows, and recapture screenshots only if the visible flow changed.
4. Before public release, repeat the privacy scan and verify that examples and golden cases remain synthetic.

## Known local-only files

Browser-test logs under `.playwright-cli/`, `.coverage`, and pytest caches are local verification artifacts and must not be committed.
