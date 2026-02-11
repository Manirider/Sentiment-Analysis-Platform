FROM python:3.9-slim

WORKDIR /app


COPY backend/requirements.txt .

RUN pip install \
    --upgrade pip \
    --default-timeout=300 \
    --retries 10 \
    -r requirements.txt


COPY backend/ backend/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
