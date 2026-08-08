import ctffr
import streamlit as st


st.set_page_config(page_title="CT-FFR Research Inference", layout="wide")
st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: Arial, sans-serif; }
    .stApp { background: #ffffff; color: #1f2937; }
    h1, h2, h3 { color: #2c5f8e; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; color: #1f2937; }
    .results-scroll { max-height: 32rem; overflow-y: auto; }
    .results-scroll table.results-table { width: 100%; border-collapse: collapse; border-top: 1.5px solid #374151 !important; border-bottom: 1.5px solid #374151 !important; }
    .results-scroll table.results-table thead th { border: 0 !important; border-bottom: 1px solid #6b7280 !important; text-align: left; background: white; }
    .results-scroll table.results-table th, .results-scroll table.results-table td { padding: 0.55rem 0.7rem; border-left: 0 !important; border-right: 0 !important; }
    .results-scroll table.results-table tbody tr { border: 0 !important; }
    .results-scroll table.results-table tbody tr td { border-top: 0 !important; border-bottom: 0 !important; background: white; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("CT-FFR research inference")
st.write("Estimate CT-derived fractional flow reserve from common coronary CTA measurements, entirely on this computer.")

if "prediction_complete" not in st.session_state:
    st.session_state.prediction_complete = False

with st.expander("Getting started", expanded=not st.session_state.prediction_complete):
    st.markdown("## Getting started")
    st.markdown(ctffr.RESEARCH_USE_STATEMENT)
    st.download_button(
        "Download synthetic sample file",
        data=ctffr.sample_file_bytes(),
        file_name="sample_case.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.markdown("1. Upload a file or enter one lesion. 2. Review validation. 3. Run and interpret the result.")
    st.dataframe(ctffr.field_table(), hide_index=True, use_container_width=True)
    st.info(ctffr.threshold_statement())
    st.write("The SHAP chart attributes this model prediction; it does not establish causality or replace clinical interpretation.")

mode = st.radio("Input mode", ("Manual entry", "Upload file"), horizontal=True)
if st.session_state.get("active_mode") != mode:
    st.session_state.active_mode = mode
    st.session_state.pop("raw_input", None)
raw = st.session_state.get("raw_input")

if mode == "Manual entry":
    defaults = ctffr.sample_case()
    with st.form("manual_case"):
        st.subheader("Enter one lesion")
        values = {}
        columns = st.columns(2)
        for index, field in enumerate(ctffr.FIELDS):
            container = columns[index % 2]
            with container:
                if field.dtype == "bool":
                    values[field.name] = st.selectbox(
                        field.label,
                        (False, True),
                        index=int(bool(defaults[field.name])),
                        format_func=lambda value: "Yes" if value else "No",
                        help=field.tooltip,
                        key=f"manual_{field.name}",
                    )
                elif field.dtype == "enum":
                    values[field.name] = st.selectbox(
                        field.label,
                        ("male", "female"),
                        index=0 if str(defaults[field.name]).lower() == "male" else 1,
                        help=field.tooltip,
                        key=f"manual_{field.name}",
                    )
                elif field.dtype in {"int", "float"}:
                    values[field.name] = st.number_input(
                        field.label,
                        min_value=int(field.minimum) if field.dtype == "int" else float(field.minimum),
                        max_value=int(field.maximum) if field.dtype == "int" else float(field.maximum),
                        value=int(defaults[field.name]) if field.dtype == "int" else float(defaults[field.name]),
                        step=1 if field.dtype == "int" else 0.1,
                        help=field.tooltip,
                        key=f"manual_{field.name}",
                    )
                else:
                    values[field.name] = st.text_input(
                        field.label,
                        value=str(defaults[field.name]),
                        help=field.tooltip,
                        key=f"manual_{field.name}",
                    )
        submitted = st.form_submit_button("Validate and run")
    if submitted:
        raw = ctffr.frame_from_records([values])
        st.session_state.raw_input = raw
else:
    upload = st.file_uploader("Upload CSV, TSV, XLSX, or XLS", type=("csv", "tsv", "xlsx", "xls"))
    if upload is not None:
        try:
            raw = ctffr.read_table(upload, upload.name)
            st.session_state.raw_input = raw
        except ValueError as error:
            st.error(str(error))
            raw = None

if raw is not None:
    st.subheader("Validation report")
    report = ctffr.validate(raw)
    st.success(f"✓ {report.n_cases} case(s) detected")
    st.success(f"✓ {report.fields_found} of {report.fields_required} required fields found")
    for issue in report.issues:
        if issue.severity == "error":
            st.error(f"✗ {issue.message}")
        else:
            st.warning(f"⚠ {issue.message}")
    if not report.blocking:
        try:
            results = ctffr.predict(raw)
            st.session_state.prediction_complete = True
            st.subheader("Results")
            if len(results) == 1:
                st.metric("Predicted CT-FFR", f"{results.loc[0, 'predicted_ctffr']:.3f}")
                st.write(ctffr.threshold_statement())
                selected_case = str(results.loc[0, "case_id"])
            else:
                st.markdown(ctffr.results_table_html(results), unsafe_allow_html=True)
                requested_case = st.selectbox("Select a case to explain", results["case_id"].astype(str).tolist())
                selected_case = requested_case if st.button("Generate explanation") else None
            download_columns = st.columns(2)
            download_columns[0].download_button("Predictions (CSV)", ctffr.prediction_bytes(results, "csv"), "ctffr_predictions.csv", "text/csv")
            download_columns[1].download_button("Predictions (XLSX)", ctffr.prediction_bytes(results, "xlsx"), "ctffr_predictions.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            if selected_case is not None:
                explanation = ctffr.explain(raw, selected_case)
                st.pyplot(ctffr.contribution_plot(explanation), clear_figure=True)
                explanation_columns = st.columns(3)
                explanation_columns[0].download_button("Contributions (CSV)", explanation.contributions.to_csv(index=False).encode("utf-8"), f"{selected_case}_contributions.csv", "text/csv")
                explanation_columns[1].download_button("Explanation (PNG)", ctffr.figure_bytes(explanation, "png"), f"{selected_case}_explanation.png", "image/png")
                explanation_columns[2].download_button("Explanation (SVG)", ctffr.figure_bytes(explanation, "svg"), f"{selected_case}_explanation.svg", "image/svg+xml")
        except ctffr.ValidationError as error:
            st.error(str(error))

st.divider()
st.caption(ctffr.RESEARCH_USE_STATEMENT)
st.caption(ctffr.CTFFR_STATEMENT)
st.caption("All processing is local. Uploaded data are held in memory and are never transmitted or written by the application.")
