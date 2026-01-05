# Guía de Docker para Framasa ERP Backend

Esta guía explica cómo construir y ejecutar el backend usando Docker.

## Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 2.0 o superior)
- **PostgreSQL instalado y corriendo localmente** (la base de datos no está en Docker)

## Configuración Inicial

1. **Asegúrate de que PostgreSQL esté corriendo localmente**

2. **Crear archivo `.env`** en la raíz del proyecto con las siguientes variables:

```env
# Django Settings
DJANGO_SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (Base de datos local)
DB_NAME=framasa_db
DB_USER=framasa_user
DB_PASSWORD=framasapass
DB_HOST=localhost
DB_PORT=5432
```

**Nota**: El contenedor Docker usará `host.docker.internal` para conectarse a la base de datos local automáticamente.

## Desarrollo

### Construir y ejecutar con Docker Compose

```bash
# Construir las imágenes
docker-compose build

# Iniciar el servicio del backend (con Gunicorn)
docker-compose up

# Ejecutar en segundo plano
docker-compose up -d

# Ver los logs
docker-compose logs -f

# Detener los servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

**Nota**: El backend se ejecuta con **Gunicorn** tanto en desarrollo como en producción.

### Comandos Útiles

```bash
# Ejecutar migraciones manualmente
docker-compose exec web python manage.py migrate

# Crear un superusuario
docker-compose exec web python manage.py createsuperuser

# Acceder al shell de Django
docker-compose exec web python manage.py shell

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic

# Ver logs del backend
docker-compose logs web
```

## Producción

### Construir la imagen

```bash
# Construir la imagen
docker build -t framasa-backend:latest .

# Ver las imágenes construidas
docker images
```

### Ejecutar con Docker Compose (Producción)

```bash
# Usar el archivo de producción
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Detener servicios
docker-compose -f docker-compose.prod.yml down
```

**Nota**: El backend se ejecuta con **Gunicorn** con 3 workers por defecto.

### Ejecutar manualmente

```bash
# Ejecutar el contenedor
docker run -d \
  --name framasa-backend \
  -p 8000:8000 \
  --env-file .env \
  --add-host=host.docker.internal:host-gateway \
  -e DB_HOST=host.docker.internal \
  framasa-backend:latest
```

## Estructura de Archivos Docker

- **Dockerfile**: Define cómo construir la imagen de la aplicación
- **docker-compose.yml**: Configuración para desarrollo
- **docker-compose.prod.yml**: Configuración para producción
- **docker-entrypoint.sh**: Script que se ejecuta al iniciar el contenedor
- **.dockerignore**: Archivos que se excluyen al construir la imagen

## Archivos Estáticos

El proyecto está configurado con **WhiteNoise** para servir archivos estáticos (CSS, JavaScript, imágenes) tanto en desarrollo como en producción. Los archivos estáticos se recopilan automáticamente al iniciar el contenedor.

### Recopilar archivos estáticos manualmente

```bash
# Dentro del contenedor
docker-compose exec web python manage.py collectstatic --noinput

# O reconstruir el contenedor
docker-compose up --build
```

## Solución de Problemas

### El contenedor no se conecta a la base de datos local

- Verifica que PostgreSQL esté corriendo localmente
- Verifica que PostgreSQL esté escuchando en el puerto 5432
- Verifica las variables de entorno en el archivo `.env` (DB_NAME, DB_USER, DB_PASSWORD)
- En Windows/Mac, el contenedor usa `host.docker.internal` automáticamente
- En Linux, si tienes problemas, puedes usar `--network="host"` en docker run

### Los archivos estáticos (CSS/JS) no se cargan en el admin

- Asegúrate de que los archivos estáticos se hayan recopilado: `docker-compose exec web python manage.py collectstatic`
- Verifica que WhiteNoise esté instalado: `docker-compose exec web pip list | grep whitenoise`
- Reconstruye el contenedor: `docker-compose up --build`
- Verifica que el directorio `staticfiles` exista y tenga permisos correctos

### Error al ejecutar migraciones

```bash
# Ejecutar migraciones manualmente
docker-compose exec web python manage.py migrate
```

### Limpiar todo y empezar de nuevo

```bash
# Detener y eliminar contenedores, redes y volúmenes
docker-compose down -v

# Eliminar imágenes
docker rmi framasa-backend

# Reconstruir desde cero
docker-compose build --no-cache
docker-compose up
```

## Puertos

- **8000**: Puerto del backend Django (Gunicorn)
- **5432**: Puerto de PostgreSQL (local, no en Docker)

## Volúmenes

- `static_volume`: Archivos estáticos de Django

## Servidor Web

El backend se ejecuta con **Gunicorn** tanto en desarrollo como en producción:
- **Desarrollo**: Gunicorn con configuración por defecto
- **Producción**: Gunicorn con 3 workers (configurable en Dockerfile)

Para cambiar el número de workers, edita el Dockerfile:
```dockerfile
CMD ["gunicorn", "framasa_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

