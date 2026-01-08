#!/bin/sh
# Wrapper para docker-entrypoint.sh que convierte CRLF a LF en tiempo de ejecución
# Esto es necesario cuando se monta un volumen desde Windows que sobrescribe el archivo

# Convertir CRLF a LF si es necesario (para volúmenes montados desde Windows)
sed -i 's/\r$//' /app/docker-entrypoint.sh 2>/dev/null || true

# Ejecutar el entrypoint original
exec /app/docker-entrypoint.sh "$@"

