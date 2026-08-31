# CT-FFR Research Inference

A local-first web, command-line, and Python application for locked continuous CT-FFR inference from common coronary CTA measurements.

> **For academic research use only. Not for clinical diagnosis or decision-making.** This software is not a medical device, has not been prospectively validated for clinical deployment, and must not be used to direct patient care.

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

The repository includes the integrity-checked fitted pipeline, an aggregate synthetic SHAP background composed of 25 k-means cluster centroids, and ten synthetic golden cases. It contains no training code or exact patient rows. The app background is not the original patient-level background used for the manuscript, so app-generated SHAP values will not exactly reproduce the paper. The stable background-dependent base value changed from 0.75341 to 0.74707 (difference, -0.00635); case-level contribution differences depend on the feature profile and permutation path and should not be interpreted as a fixed global offset. Run:

```bash
pip install -e ".[test]"
pytest --cov=ctffr --cov-report=term-missing
```

Technical details, validation posture, and the quantified centroid-background SHAP difference are in [Model documentation](docs/MODEL.md).

## License, intended use, and citation

The code is released under the [MIT License](LICENSE). MIT is a permissive open-source license and does not itself impose an academic-only or noncommercial restriction. Independently of that license, the authors' intended-use notice is explicit: this research prototype is for academic research and software evaluation only; it is not a medical device and must not be used for clinical diagnosis, treatment selection, or any patient-care decision.

`CITATION.cff` contains explicit placeholders pending the project owner's author list, ORCIDs, paper metadata, DOI, and repository URL. Complete those fields before public release.
