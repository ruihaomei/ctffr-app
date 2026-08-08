# CT-FFR Research Inference

A local-first web, command-line, and Python application for locked continuous CT-FFR inference from common coronary CTA measurements.

> **For research use only.** This software is not a medical device and is not intended for standalone clinical diagnosis or treatment decisions.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
streamlit run app/streamlit_app.py
```

![Single-case application view](docs/images/single_case.png)

[Open the visual three-minute demo](docs/DEMO.md) for a screenshot-led single-case and batch walkthrough.

The model estimates CT-derived fractional flow reserve. CT-FFR is itself a computational estimate of invasive fractional flow reserve; this software does not predict invasive FFR.

## What it does

Enter one lesion or upload CSV, TSV, XLSX, or XLS data. The application validates all rows, derives model inputs, reports continuous predicted CT-FFR, and provides a per-lesion SHAP explanation. Batch predictions and individual explanations can be downloaded as CSV/XLSX and PNG/SVG. All processing is local: the app performs no network calls, telemetry, or server uploads, and it does not write uploaded patient data to disk.

![Batch application view](docs/images/batch.png)

The public samples are hand-authored synthetic lesions. No row-level development or external-cohort records are included. See the [guided demo](docs/DEMO.md), [quick start](docs/QUICKSTART.md), [input format](docs/INPUT_FORMAT.md), and generated [data dictionary](docs/DATA_DICTIONARY.md).

## Command line

```bash
ctffr validate --input examples/sample_case.xlsx
ctffr predict --input examples/sample_batch.csv --output predictions.xlsx
ctffr explain --input examples/sample_case.xlsx --case-id SYN-001 --output explanation.png
```

The same `ctffr.predict()` implementation serves the Python API, CLI, and web app.

## Docker

```bash
docker build -t ctffr .
docker run --rm -p 8501:8501 ctffr
```

Open `http://localhost:8501`. Data remain inside the local container.

## Model and testing

The repository includes the integrity-checked fitted pipeline, an aggregate 25-centroid SHAP background, and ten synthetic golden cases. It contains no training code. Run:

```bash
pytest --cov=ctffr --cov-report=term-missing
```

Technical details, validation posture, and the quantified centroid-background SHAP difference are in [Model documentation](docs/MODEL.md).

## Citation and licence

`CITATION.cff` contains explicit placeholders pending the project owner's author list, ORCIDs, paper metadata, DOI, and repository URL. `LICENSE` intentionally remains `LICENCE TBD` until the project owner selects a licence. Do not publish this repository before both are finalized.
