FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install psycopg2-binary && \
    apt-get update && apt-get install -y curl

COPY app/ app/

ENV PYTHONPATH=/app

CMD ["streamlit", "run", "app/streamlit_app.py"]