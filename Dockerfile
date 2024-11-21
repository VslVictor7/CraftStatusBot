FROM python:3.11-slim

WORKDIR /app

# Atualizar pacotes e instalar dependências essenciais
RUN apt-get update && apt-get install -y \
    && apt-get clean

# Copiar as dependências do projeto
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto para dentro do container
COPY . .

# Copiar variáveis de ambiente (opcional, substitua pelo seu gerenciador de envs)
COPY .env .env

# Comando para rodar o bot
CMD ["python", "bot/core/main.py"]