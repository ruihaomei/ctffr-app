# Three-Minute Quick Start

Prefer a screenshot-led walkthrough? Open the [guided demo](DEMO.md).

## Install and open

1. Install Python 3.12 from python.org.
2. Download this repository and open a terminal in its folder.
3. Run:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
streamlit run app/streamlit_app.py
```

Your browser opens the local application. No account or internet connection is needed after installation.

## Make the first prediction

1. Expand **Getting started** and download the synthetic sample.
2. Select **Upload file**, upload `sample_case.xlsx`, and review the validation report.
3. Read the predicted CT-FFR and SHAP contribution chart, then download results if needed.

Warnings identify extrapolation beyond values observed in the study cohorts but do not block prediction. Errors identify the row and field to fix.

The threshold category is a reporting convention, not a diagnosis. SHAP describes this model's local attribution and does not establish causality.
