FROM python:3.12.8-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot/core/main.py"]