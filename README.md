# Backend FRAMASA ERP - Django REST Framework

API REST para el sistema ERP multiempresa FRAMASA.

## 🚀 Inicio Rápido

### 1. Configurar Entorno Virtual

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

1. Crear base de datos PostgreSQL:
```sql
CREATE DATABASE framasa_db;
```

2. Crear archivo `.env` en la raíz del backend:
```env
DJANGO_SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=framasa_db
DB_USER=postgres
DB_PASSWORD=tu-password-postgres
DB_HOST=localhost
DB_PORT=5432
```

### 4. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 5. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 6. Iniciar Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en `http://127.0.0.1:8000`

## 📁 Estructura del Proyecto

```
backend/
├── authentication/     # Autenticación y usuarios
├── ferreteria/         # Módulo de ferretería
├── bloquera/           # Módulo de bloquera
├── piedrinera/         # Módulo de piedrinera
├── planillas/          # Módulo de planillas
├── productos/          # Productos compartidos
└── framasa_backend/    # Configuración principal
    ├── settings.py     # Configuraciones
    ├── urls.py         # URLs principales
    └── wsgi.py         # WSGI config
```

## 🔐 Autenticación

El sistema usa JWT (JSON Web Tokens) para autenticación.

### Endpoints de Autenticación

- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/verify/` - Verificar token
- `POST /api/auth/logout/` - Cerrar sesión

### Uso

```python
# Login
POST /api/auth/login/
{
    "username": "usuario",
    "password": "password"
}

# Respuesta
{
    "access": "token-jwt-aqui",
    "refresh": "refresh-token-aqui"
}

# Usar token en requests
Authorization: Bearer token-jwt-aqui
```

## 📚 Apps del Sistema

### Authentication
- Gestión de usuarios
- Autenticación JWT
- Permisos y roles

### Ferreteria
- Productos
- Clientes
- Ventas
- Inventario
- Reportes

### Bloquera
- Productos (bloques)
- Producción
- Inventario

### Piedrinera
- Productos (agregados)
- Camiones
- Despachos
- Inventario

### Planillas
- Empleados
- Asistencias
- Nóminas

## 🛠️ Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell

# Ejecutar tests
python manage.py test

# Recolectar archivos estáticos
python manage.py collectstatic
```

## 📦 Dependencias Principales

- Django 5.0+
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- psycopg2 (PostgreSQL)
- python-dotenv

## 🔧 Configuración

Ver `framasa_backend/settings.py` para todas las configuraciones.

Variables de entorno importantes:
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (True/False)
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `ALLOWED_HOSTS`: Hosts permitidos (separados por comas)
- `CORS_ALLOWED_ORIGINS`: Orígenes permitidos para CORS

## 📝 Notas

- El backend corre en el puerto 8000 por defecto
- Usa PostgreSQL como base de datos principal
- JWT tokens expiran después de cierto tiempo (configurable)
- CORS está configurado para permitir requests del frontend


