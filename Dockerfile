FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk update && \
    apk add --no-cache gcc musl-dev libffi-dev git postgresql-dev libpq && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev libffi-dev postgresql-dev git && \
    rm -rf /var/cache/apk/*

COPY . .

CMD ["python", "bot/core/main.py"]