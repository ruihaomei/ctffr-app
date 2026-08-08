FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app
COPY requirements.txt pyproject.toml README.md LICENSE ./
COPY ctffr ./ctffr
COPY artifacts ./artifacts
COPY examples ./examples
COPY app ./app
RUN pip install --no-cache-dir .

EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]

