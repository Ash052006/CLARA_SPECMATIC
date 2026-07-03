# Lightweight Docker image for Clara Specmatic workflows.
# This image intentionally runs Clara with CLARA_CONTRACT_TEST_MODE=1, so it
# does not install the heavy AI, ChromaDB, or Google API runtime packages.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CLARA_CONTRACT_TEST_MODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git nodejs npm default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.docker.txt ./
RUN pip install --no-cache-dir -r requirements.docker.txt

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

EXPOSE 8000 9000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
