# ======================
# STAGE 1 — BUILD
# ======================
FROM python:3.14.2-alpine AS builder

WORKDIR /build

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev libffi-dev && \
    python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ======================
# STAGE 2 — PROD
# ======================
FROM python:3.14.2-alpine

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

CMD ["python", "bot/core/main.py"]