FROM python:3.9-slim

WORKDIR /app

COPY backend backend
COPY ingester ingester
COPY ingester/requirements.txt .

ENV PYTHONPATH=/app

RUN pip install \
    --upgrade pip \
    --default-timeout=300 \
    --retries 10 \
    -r requirements.txt

CMD ["python", "ingester/ingester.py"]
