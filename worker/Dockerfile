FROM python:3.9-slim

WORKDIR /app
ENV PYTHONPATH=/app
COPY backend backend
COPY worker worker
COPY worker/requirements.txt .
ENV DATABASE_URL=${DATABASE_URL}


RUN pip install --upgrade pip && \
    pip install --default-timeout=300 torch --index-url https://download.pytorch.org/whl/cpu


RUN pip install --default-timeout=300 -r requirements.txt

CMD ["python", "worker/worker.py"]
