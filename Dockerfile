# Usar imagen base de Python
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de requisitos
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Exponer el puerto
EXPOSE 8000

# Script de inicio (convertir CRLF a LF para compatibilidad Windows/Linux)
COPY docker-entrypoint.sh /app/
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Copiar script wrapper que convierte el entrypoint en tiempo de ejecución
# (necesario cuando se monta un volumen que sobrescribe el archivo)
COPY entrypoint-wrapper.sh /app/
RUN sed -i 's/\r$//' /app/entrypoint-wrapper.sh && chmod +x /app/entrypoint-wrapper.sh

# Comando por defecto
ENTRYPOINT ["/app/entrypoint-wrapper.sh"]
CMD ["gunicorn", "framasa_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

