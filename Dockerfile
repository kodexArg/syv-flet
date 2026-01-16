FROM python:3.13-slim

WORKDIR /app

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    DEBUG=True

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src
COPY assets/ ./assets

# Crear directorio de logs (volumen)
RUN mkdir -p /app/logs

# Comando default
CMD ["python", "-m", "src.main"]
