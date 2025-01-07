FROM python:3.12.8-alpine

WORKDIR /app

COPY . .

RUN apk update && \
    apk add --no-cache && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/cache/apk/*

CMD ["python", "bot/core/main.py"]