FROM python:3.11-alpine

WORKDIR /app

# Atualizando os pacotes base e instale dependências necessárias
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .

RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot/core/main.py"]