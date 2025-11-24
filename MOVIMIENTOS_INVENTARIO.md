# Documentación de Movimientos de Inventario

Este sistema permite gestionar movimientos de inventario para tres tipos de productos:
- **Ferretería**: Productos de ferretería (unidades enteras)
- **Bloquera**: Productos de bloquera (unidades enteras)
- **Piedrinera**: Agregados de piedrinera (metros cúbicos con decimales)

## Endpoints Disponibles

### Ferretería
```
http://localhost:8000/api/ferreteria/movimientos-inventario/
```

### Bloquera
```
http://localhost:8000/api/bloquera/movimientos-inventario/
```

### Piedrinera
```
http://localhost:8000/api/piedrinera/movimientos-inventario/
```

---

## 1. Listar Movimientos (GET)

### Endpoints
- **Ferretería**: `GET /api/ferreteria/movimientos-inventario/`
- **Bloquera**: `GET /api/bloquera/movimientos-inventario/`
- **Piedrinera**: `GET /api/piedrinera/movimientos-inventario/`

### Headers Requeridos
```
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

### Parámetros de Filtro (Query Parameters - Opcionales)
- `producto`: ID del producto (número)
- `tipo`: Tipo de movimiento (ENTRADA, SALIDA, AJUSTE, TRANSFERENCIA, DEVOLUCION)
- `fecha_desde`: Fecha desde (formato: YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (formato: YYYY-MM-DD)
- `page`: Número de página (para paginación)

### Ejemplos de Requests

#### Listar todos los movimientos de ferretería
```http
GET /api/ferreteria/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Listar todos los movimientos de bloquera
```http
GET /api/bloquera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Listar todos los movimientos de piedrinera
```http
GET /api/piedrinera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Filtrar por producto
```http
GET /api/ferreteria/movimientos-inventario/?producto=1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Filtrar por tipo de movimiento
```http
GET /api/bloquera/movimientos-inventario/?tipo=ENTRADA
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Filtrar por rango de fechas
```http
GET /api/piedrinera/movimientos-inventario/?fecha_desde=2025-01-01&fecha_hasta=2025-01-31
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Combinar múltiples filtros
```http
GET /api/ferreteria/movimientos-inventario/?producto=1&tipo=SALIDA&fecha_desde=2025-01-01
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Respuesta (Ejemplo - Ferretería/Bloquera)
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/ferreteria/movimientos-inventario/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "producto": {
        "id": 1,
        "codigo": "PROD001",
        "nombre": "Martillo"
      },
      "producto_id": 1,
      "tipo": "ENTRADA",
      "tipoDisplay": "Entrada",
      "cantidad": 10,
      "stockAnterior": 5,
      "stockNuevo": 15,
      "motivo": "Compra a proveedor",
      "observaciones": "Lote nuevo",
      "usuario": {
        "id": 1,
        "nombre": "admin"
      },
      "usuario_id": 1,
      "fechaMovimiento": "2025-01-15T10:30:00Z",
      "fecha_movimiento": "2025-01-15T10:30:00Z",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Respuesta (Ejemplo - Piedrinera)
```json
{
  "count": 30,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "producto": {
        "id": 1,
        "codigo": "ARENA001",
        "nombre": "Arena Fina"
      },
      "producto_id": 1,
      "tipo": "ENTRADA",
      "tipoDisplay": "Entrada",
      "cantidad": 25.5,
      "stockAnterior": 100.0,
      "stockNuevo": 125.5,
      "motivo": "Extracción",
      "observaciones": "Cantera Norte",
      "usuario": {
        "id": 1,
        "nombre": "admin"
      },
      "usuario_id": 1,
      "fechaMovimiento": "2025-01-15T10:30:00Z",
      "fecha_movimiento": "2025-01-15T10:30:00Z",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**Nota**: En piedrinera, las cantidades se manejan en metros cúbicos (m³) y pueden tener decimales.

---

## 2. Obtener Detalle de un Movimiento (GET)

### Endpoints
- **Ferretería**: `GET /api/ferreteria/movimientos-inventario/{id}/`
- **Bloquera**: `GET /api/bloquera/movimientos-inventario/{id}/`
- **Piedrinera**: `GET /api/piedrinera/movimientos-inventario/{id}/`

### Ejemplo
```http
GET /api/ferreteria/movimientos-inventario/1/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Respuesta
```json
{
  "id": 1,
  "producto": {
    "id": 1,
    "codigo": "PROD001",
    "nombre": "Martillo"
  },
  "producto_id": 1,
  "tipo": "ENTRADA",
  "tipoDisplay": "Entrada",
  "cantidad": 10,
  "stockAnterior": 5,
  "stockNuevo": 15,
  "motivo": "Compra a proveedor",
  "observaciones": "Lote nuevo",
  "usuario": {
    "id": 1,
    "nombre": "admin"
  },
  "usuario_id": 1,
  "fechaMovimiento": "2025-01-15T10:30:00Z",
  "fecha_movimiento": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## 3. Crear Movimiento (POST)

### Endpoints
- **Ferretería**: `POST /api/ferreteria/movimientos-inventario/`
- **Bloquera**: `POST /api/bloquera/movimientos-inventario/`
- **Piedrinera**: `POST /api/piedrinera/movimientos-inventario/`

### Headers Requeridos
```
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

### Body del Request

#### Campos Requeridos
- `producto_id`: ID del producto (número)
- `tipo`: Tipo de movimiento (ENTRADA, SALIDA, AJUSTE, TRANSFERENCIA, DEVOLUCION)
- `cantidad`: Cantidad del movimiento
  - **Ferretería/Bloquera**: Número entero positivo (unidades)
  - **Piedrinera**: Número decimal positivo (metros cúbicos)

#### Campos Opcionales
- `motivo`: Motivo del movimiento (string, máximo 200 caracteres)
- `observaciones`: Observaciones adicionales (texto)

**Nota:** El `usuario` se asigna automáticamente desde el token JWT. No es necesario enviarlo.

### Tipos de Movimiento Disponibles
- `ENTRADA`: Incrementa el stock (cantidad debe ser > 0)
- `SALIDA`: Decrementa el stock (cantidad debe ser > 0, verifica stock suficiente)
- `AJUSTE`: Ajuste de inventario (cantidad puede ser positiva o negativa)
- `TRANSFERENCIA`: Transferencia a otra ubicación (cantidad debe ser > 0, verifica stock suficiente)
- `DEVOLUCION`: Devolución de producto (cantidad debe ser > 0)

### Ejemplos de Requests

#### 1. Entrada de Inventario (Ferretería)
```http
POST /api/ferreteria/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "ENTRADA",
  "cantidad": 50,
  "motivo": "Compra a proveedor",
  "observaciones": "Lote #12345"
}
```

#### 2. Entrada de Inventario (Bloquera)
```http
POST /api/bloquera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "ENTRADA",
  "cantidad": 100,
  "motivo": "Producción",
  "observaciones": "Lote diario"
}
```

#### 3. Entrada de Inventario (Piedrinera)
```http
POST /api/piedrinera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "ENTRADA",
  "cantidad": 25.5,
  "motivo": "Extracción",
  "observaciones": "Cantera Norte"
}
```

#### 4. Salida de Inventario
```http
POST /api/ferreteria/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "SALIDA",
  "cantidad": 10,
  "motivo": "Venta",
  "observaciones": "Factura #001"
}
```

#### 5. Ajuste de Inventario (Incremento)
```http
POST /api/bloquera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "AJUSTE",
  "cantidad": 5,
  "motivo": "Conteo físico",
  "observaciones": "Diferencia encontrada en inventario"
}
```

#### 6. Ajuste de Inventario (Decremento)
```http
POST /api/ferreteria/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "AJUSTE",
  "cantidad": -3,
  "motivo": "Pérdida por daño",
  "observaciones": "Productos dañados en almacén"
}
```

#### 7. Ajuste de Inventario (Piedrinera - Decremento)
```http
POST /api/piedrinera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "AJUSTE",
  "cantidad": -2.5,
  "motivo": "Pérdida por evaporación",
  "observaciones": "Ajuste por humedad"
}
```

#### 8. Devolución
```http
POST /api/ferreteria/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "DEVOLUCION",
  "cantidad": 2,
  "motivo": "Devolución de cliente",
  "observaciones": "Cliente no satisfecho"
}
```

#### 9. Transferencia
```http
POST /api/bloquera/movimientos-inventario/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "producto_id": 1,
  "tipo": "TRANSFERENCIA",
  "cantidad": 20,
  "motivo": "Transferencia a sucursal",
  "observaciones": "Sucursal Centro"
}
```

### Respuesta Exitosa (201 Created)
```json
{
  "id": 1,
  "producto": {
    "id": 1,
    "codigo": "PROD001",
    "nombre": "Martillo"
  },
  "producto_id": 1,
  "tipo": "ENTRADA",
  "tipoDisplay": "Entrada",
  "cantidad": 50,
  "stockAnterior": 10,
  "stockNuevo": 60,
  "motivo": "Compra a proveedor",
  "observaciones": "Lote #12345",
  "usuario": {
    "id": 1,
    "nombre": "admin"
  },
  "usuario_id": 1,
  "fechaMovimiento": "2025-01-15T10:30:00Z",
  "fecha_movimiento": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Errores Posibles

#### Stock Insuficiente (400 Bad Request)
```json
{
  "cantidad": ["Stock insuficiente. Stock actual: 5"]
}
```

#### Cantidad Inválida (400 Bad Request)
```json
{
  "cantidad": ["La cantidad debe ser mayor a 0 para este tipo de movimiento"]
}
```

#### Producto No Encontrado (400 Bad Request)
```json
{
  "producto_id": ["Invalid pk \"999\" - object does not exist."]
}
```

---

## 4. Obtener Tipos de Movimiento (GET)

### Endpoints
- **Ferretería**: `GET /api/ferreteria/movimientos-inventario/tipos/`
- **Bloquera**: `GET /api/bloquera/movimientos-inventario/tipos/`
- **Piedrinera**: `GET /api/piedrinera/movimientos-inventario/tipos/`

### Ejemplo
```http
GET /api/ferreteria/movimientos-inventario/tipos/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Respuesta
```json
[
  {
    "value": "ENTRADA",
    "label": "Entrada"
  },
  {
    "value": "SALIDA",
    "label": "Salida"
  },
  {
    "value": "AJUSTE",
    "label": "Ajuste"
  },
  {
    "value": "TRANSFERENCIA",
    "label": "Transferencia"
  },
  {
    "value": "DEVOLUCION",
    "label": "Devolución"
  }
]
```

---

## 5. Editar Movimiento (PUT/PATCH) - NO PERMITIDO

Los movimientos **NO se pueden editar** después de creados en ninguno de los tres sistemas.

### Respuesta
```json
{
  "error": "Los movimientos de inventario no se pueden editar"
}
```
**Status Code:** 405 Method Not Allowed

---

## 6. Eliminar Movimiento (DELETE) - NO PERMITIDO

Los movimientos **NO se pueden eliminar** después de creados en ninguno de los tres sistemas.

### Respuesta
```json
{
  "error": "Los movimientos de inventario no se pueden eliminar"
}
```
**Status Code:** 405 Method Not Allowed

---

## Comportamiento Automático

### Actualización de Stock
Cuando se crea un movimiento, el stock del producto se actualiza automáticamente:

- **ENTRADA**: `stock_nuevo = stock_anterior + cantidad`
- **SALIDA**: `stock_nuevo = max(0, stock_anterior - cantidad)`
- **AJUSTE**: `stock_nuevo = max(0, stock_anterior + cantidad)` (cantidad puede ser negativa)
- **DEVOLUCION**: `stock_nuevo = stock_anterior + cantidad`
- **TRANSFERENCIA**: `stock_nuevo = max(0, stock_anterior - cantidad)`

### Asignación de Usuario
El usuario se asigna automáticamente desde el token JWT del request. No es necesario enviarlo en el body.

### Registro de Stock
Cada movimiento registra:
- `stock_anterior`: Stock antes del movimiento
- `stock_nuevo`: Stock después del movimiento
- `fecha_movimiento`: Fecha y hora del movimiento (automático)

### Diferencias entre Sistemas

#### Ferretería y Bloquera
- Cantidades en **unidades enteras** (IntegerField)
- Stock se maneja como números enteros
- Ejemplo: 50 unidades, 100 bloques

#### Piedrinera
- Cantidades en **metros cúbicos** (DecimalField)
- Stock se maneja como números decimales
- Ejemplo: 25.5 m³, 100.75 m³

---

## Ejemplos con cURL

### Crear Entrada (Ferretería)
```bash
curl -X POST http://localhost:8000/api/ferreteria/movimientos-inventario/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "producto_id": 1,
    "tipo": "ENTRADA",
    "cantidad": 50,
    "motivo": "Compra a proveedor",
    "observaciones": "Lote nuevo"
  }'
```

### Crear Entrada (Bloquera)
```bash
curl -X POST http://localhost:8000/api/bloquera/movimientos-inventario/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "producto_id": 1,
    "tipo": "ENTRADA",
    "cantidad": 100,
    "motivo": "Producción",
    "observaciones": "Lote diario"
  }'
```

### Crear Entrada (Piedrinera)
```bash
curl -X POST http://localhost:8000/api/piedrinera/movimientos-inventario/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "producto_id": 1,
    "tipo": "ENTRADA",
    "cantidad": 25.5,
    "motivo": "Extracción",
    "observaciones": "Cantera Norte"
  }'
```

### Listar Movimientos de un Producto
```bash
curl -X GET "http://localhost:8000/api/ferreteria/movimientos-inventario/?producto=1" \
  -H "Authorization: Bearer tu_token_jwt"
```

### Obtener Tipos de Movimiento
```bash
curl -X GET http://localhost:8000/api/ferreteria/movimientos-inventario/tipos/ \
  -H "Authorization: Bearer tu_token_jwt"
```

---

## Ejemplos con JavaScript (Fetch)

### Crear Movimiento (Ferretería)
```javascript
const crearMovimiento = async (productoId, tipo, cantidad, motivo, observaciones) => {
  const response = await fetch('http://localhost:8000/api/ferreteria/movimientos-inventario/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      producto_id: productoId,
      tipo: tipo,
      cantidad: cantidad,
      motivo: motivo,
      observaciones: observaciones
    })
  });
  
  return await response.json();
};

// Ejemplo de uso
crearMovimiento(1, 'ENTRADA', 50, 'Compra a proveedor', 'Lote nuevo');
```

### Crear Movimiento (Piedrinera)
```javascript
const crearMovimientoPiedrinera = async (productoId, tipo, cantidad, motivo, observaciones) => {
  const response = await fetch('http://localhost:8000/api/piedrinera/movimientos-inventario/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      producto_id: productoId,
      tipo: tipo,
      cantidad: cantidad, // Decimal para piedrinera (ej: 25.5)
      motivo: motivo,
      observaciones: observaciones
    })
  });
  
  return await response.json();
};

// Ejemplo de uso
crearMovimientoPiedrinera(1, 'ENTRADA', 25.5, 'Extracción', 'Cantera Norte');
```

### Listar Movimientos con Filtros
```javascript
const listarMovimientos = async (sistema, filtros = {}) => {
  const baseUrl = `http://localhost:8000/api/${sistema}/movimientos-inventario/`;
  const params = new URLSearchParams(filtros);
  const response = await fetch(`${baseUrl}?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};

// Ejemplos de uso
listarMovimientos('ferreteria', { producto: 1 });
listarMovimientos('bloquera', { tipo: 'ENTRADA', fecha_desde: '2025-01-01' });
listarMovimientos('piedrinera', { tipo: 'SALIDA' });
```

---

## Resumen de Endpoints

| Sistema | Base URL | Descripción |
|---------|----------|-------------|
| **Ferretería** | `/api/ferreteria/movimientos-inventario/` | Productos de ferretería (unidades enteras) |
| **Bloquera** | `/api/bloquera/movimientos-inventario/` | Productos de bloquera (unidades enteras) |
| **Piedrinera** | `/api/piedrinera/movimientos-inventario/` | Agregados de piedrinera (metros cúbicos) |

Todos los endpoints comparten la misma estructura y funcionalidad, con la única diferencia en el tipo de datos para las cantidades (enteros vs decimales).
