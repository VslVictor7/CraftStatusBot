FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add --no-cache gcc musl-dev libffi-dev git && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev libffi-dev

COPY . .

CMD ["python", "bot/core/main.py"]