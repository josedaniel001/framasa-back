#!/bin/sh
set -e

# Esperar a que la base de datos local esté lista
echo "Esperando a que la base de datos esté lista..."
DB_HOST=${DB_HOST:-host.docker.internal}
DB_PORT=${DB_PORT:-5432}

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Esperando conexión a $DB_HOST:$DB_PORT..."
  sleep 1
done
echo "Base de datos lista!"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Ejecutar el comando pasado como argumento
exec "$@"

