# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY load_to_postgres.py .
# Do NOT copy data/ — it will be mounted at runtime

CMD ["python", "load_to_postgres.py"]