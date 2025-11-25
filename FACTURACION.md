# Documentación de Facturación Unificada

Este sistema permite crear facturas que pueden incluir productos de las tres empresas (Ferretería, Bloquera y Piedrinera) en una sola factura, con soporte para múltiples formas de pago.

## Base URL
```
http://localhost:8000/api/facturacion/
```

---

## 1. Crear Factura (POST)

### Endpoint
```
POST /api/facturacion/facturas/
```

### Descripción
Crea una factura que puede incluir productos de las tres empresas en el mismo request. El sistema detecta automáticamente si hay productos de múltiples empresas y asigna el prefijo "MIXT" al número de factura.

### Headers Requeridos
```
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

### Body del Request

#### Campos Requeridos
- `cliente`: ID del cliente (número)
- `detalles`: Array de objetos con los productos a facturar

#### Campos Opcionales
- `empresa`: Empresa principal (FERRETERIA, BLOQUERA, PIEDRINERA, MIXTA). Si no se especifica y hay productos de múltiples empresas, se usa automáticamente "MIXTA"
- `descuento`: Descuento general de la factura (decimal, default: 0)
- `observaciones`: Observaciones adicionales (texto)
- `fecha_vencimiento`: Fecha de vencimiento para crédito (YYYY-MM-DD)

#### Estructura de Detalles
Cada detalle debe incluir:
- `producto_id`: ID del producto (número)
- `producto_empresa`: Empresa del producto (FERRETERIA, BLOQUERA, PIEDRINERA)
- `cantidad`: Cantidad a vender (decimal para piedrinera, entero para ferretería/bloquera)
- `precio_unitario`: Precio unitario (opcional, si no se proporciona usa el precio del producto)
- `descuento`: Descuento del detalle (decimal, default: 0)

### Ejemplos de Requests

#### Factura con productos de una sola empresa (Ferretería)
```json
POST /api/facturacion/facturas/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "empresa": "FERRETERIA",
  "cliente": 1,
  "descuento": 0,
  "observaciones": "Venta normal",
  "detalles": [
    {
      "producto_id": 1,
      "producto_empresa": "FERRETERIA",
      "cantidad": 10,
      "precio_unitario": 50.00,
      "descuento": 0
    },
    {
      "producto_id": 2,
      "producto_empresa": "FERRETERIA",
      "cantidad": 5,
      "precio_unitario": 25.00,
      "descuento": 0
    }
  ]
}
```

#### Factura MIXTA con productos de las 3 empresas
```json
POST /api/facturacion/facturas/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "cliente": 1,
  "descuento": 50.00,
  "observaciones": "Venta mixta - productos de las 3 empresas",
  "detalles": [
    {
      "producto_id": 1,
      "producto_empresa": "FERRETERIA",
      "cantidad": 10,
      "precio_unitario": 50.00,
      "descuento": 0
    },
    {
      "producto_id": 5,
      "producto_empresa": "BLOQUERA",
      "cantidad": 100,
      "precio_unitario": 5.00,
      "descuento": 0
    },
    {
      "producto_id": 3,
      "producto_empresa": "PIEDRINERA",
      "cantidad": 25.5,
      "precio_unitario": 100.00,
      "descuento": 0
    }
  ]
}
```

**Nota:** Si incluyes productos de múltiples empresas, el sistema automáticamente:
- Asigna `empresa: "MIXTA"` a la factura
- Genera un número de factura con prefijo "MIXT" (ej: MIXT000001)

### Respuesta Exitosa (201 Created)
```json
{
  "id": 1,
  "numero_factura": "MIXT000001",
  "empresa": "MIXTA",
  "empresa_display": "Mixta (Múltiples Empresas)",
  "cliente": 1,
  "cliente_id": 1,
  "cliente_nombre": "Juan Pérez",
  "cliente_nit": "12345678-9",
  "subtotal": 3000.00,
  "descuento": 50.00,
  "total": 2950.00,
  "total_pagado": 0.00,
  "saldo_pendiente": 2950.00,
  "estado": "PENDIENTE",
  "estado_display": "Pendiente de Pago",
  "observaciones": "Venta mixta - productos de las 3 empresas",
  "usuario": 1,
  "usuario_id": 1,
  "usuario_nombre": "admin",
  "fecha_factura": "2025-01-20T10:30:00Z",
  "fecha_vencimiento": null,
  "detalles": [
    {
      "id": 1,
      "factura": 1,
      "producto_id": 1,
      "producto_empresa": "FERRETERIA",
      "producto_codigo": "PROD001",
      "producto_nombre": "Martillo",
      "cantidad": 10,
      "precio_unitario": 50.00,
      "descuento": 0,
      "subtotal": 500.00
    },
    {
      "id": 2,
      "factura": 1,
      "producto_id": 5,
      "producto_empresa": "BLOQUERA",
      "producto_codigo": "BLOQ005",
      "producto_nombre": "Bloque 15x20x40",
      "cantidad": 100,
      "precio_unitario": 5.00,
      "descuento": 0,
      "subtotal": 500.00
    },
    {
      "id": 3,
      "factura": 1,
      "producto_id": 3,
      "producto_empresa": "PIEDRINERA",
      "producto_codigo": "ARENA001",
      "producto_nombre": "Arena Fina",
      "cantidad": 25.5,
      "precio_unitario": 100.00,
      "descuento": 0,
      "subtotal": 2550.00
    }
  ],
  "pagos": [],
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

---

## 2. Agregar Pagos Múltiples (POST)

### Endpoint
```
POST /api/facturacion/facturas/{id}/agregar_pagos_multiples/
```

### Descripción
Permite agregar múltiples pagos de diferentes tipos (efectivo, tarjeta, fiado) a una factura en una sola operación.

### Body del Request
```json
{
  "pagos": [
    {
      "tipo_pago": "EFECTIVO",
      "monto": 1000.00,
      "referencia": "",
      "observaciones": "Pago en efectivo"
    },
    {
      "tipo_pago": "TARJETA",
      "monto": 500.00,
      "referencia": "****1234",
      "observaciones": "Pago con tarjeta de crédito"
    },
    {
      "tipo_pago": "FIADO",
      "monto": 1450.00,
      "observaciones": "Resto a crédito"
    }
  ]
}
```

### Validaciones
- La suma de todos los pagos no puede exceder el saldo pendiente
- Para pagos a fiado, se valida que el cliente tenga crédito disponible
- El cliente debe tener `permite_fiado = true` para pagos a fiado

### Respuesta
```json
{
  "factura": {
    "id": 1,
    "numero_factura": "MIXT000001",
    "total": 2950.00,
    "total_pagado": 2950.00,
    "saldo_pendiente": 0.00,
    "estado": "PAGADA",
    ...
  },
  "pagos_creados": [
    {
      "id": 1,
      "tipo_pago": "EFECTIVO",
      "monto": 1000.00,
      ...
    },
    {
      "id": 2,
      "tipo_pago": "TARJETA",
      "monto": 500.00,
      ...
    },
    {
      "id": 3,
      "tipo_pago": "FIADO",
      "monto": 1450.00,
      ...
    }
  ]
}
```

---

## 3. Listar Facturas (GET)

### Endpoint
```
GET /api/facturacion/facturas/
```

### Parámetros de Filtro (Query Parameters - Opcionales)
- `cliente`: ID del cliente
- `empresa`: Empresa (FERRETERIA, BLOQUERA, PIEDRINERA, MIXTA)
- `estado`: Estado de la factura (BORRADOR, PENDIENTE, PARCIAL, PAGADA, ANULADA)
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)
- `numero`: Búsqueda por número de factura (parcial)

### Ejemplo
```http
GET /api/facturacion/facturas/?empresa=MIXTA&estado=PENDIENTE&fecha_desde=2025-01-01
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 4. Obtener Detalle de Factura (GET)

### Endpoint
```
GET /api/facturacion/facturas/{id}/
```

### Respuesta
Incluye todos los detalles de la factura, incluyendo productos de todas las empresas y todos los pagos registrados.

---

## 5. Agregar un Pago Individual (POST)

### Endpoint
```
POST /api/facturacion/facturas/{id}/agregar_pago/
```

### Body
```json
{
  "tipo_pago": "EFECTIVO",
  "monto": 500.00,
  "referencia": "",
  "observaciones": "Pago parcial"
}
```

---

## 6. Anular Factura (POST)

### Endpoint
```
POST /api/facturacion/facturas/{id}/anular/
```

### Descripción
Anula una factura y revierte los movimientos de inventario. Solo se puede anular si no tiene pagos registrados.

### Respuesta
```json
{
  "id": 1,
  "numero_factura": "MIXT000001",
  "estado": "ANULADA",
  ...
}
```

---

## 7. Estadísticas de Facturación (GET)

### Endpoint
```
GET /api/facturacion/facturas/estadisticas/
```

### Parámetros Opcionales
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)

### Respuesta
```json
{
  "total_facturas": 150,
  "total_ventas": 250000.50,
  "total_pagado": 200000.00,
  "total_pendiente": 50000.50,
  "por_estado": [
    {
      "estado": "PAGADA",
      "count": 100,
      "total": 200000.00
    },
    {
      "estado": "PENDIENTE",
      "count": 30,
      "total": 30000.00
    }
  ],
  "por_empresa": [
    {
      "empresa": "MIXTA",
      "count": 50,
      "total": 100000.00
    },
    {
      "empresa": "FERRETERIA",
      "count": 60,
      "total": 80000.00
    }
  ]
}
```

---

## Comportamiento Automático

### Detección de Factura Mixta
- Si en los `detalles` hay productos de más de una empresa, el sistema automáticamente:
  - Asigna `empresa: "MIXTA"` a la factura
  - Genera número de factura con prefijo "MIXT" (ej: MIXT000001)

### Actualización de Stock
- Al crear la factura, se actualiza automáticamente el stock de cada producto
- Se crean movimientos de inventario de tipo SALIDA para cada producto
- Si se anula la factura, se revierten los movimientos (entrada de stock)

### Actualización de Totales
- Los totales se calculan automáticamente:
  - `subtotal` = suma de subtotales de detalles
  - `total` = subtotal - descuento general
  - `saldo_pendiente` = total - total_pagado

### Actualización de Saldo del Cliente
- Al registrar un pago a fiado, se actualiza automáticamente el `saldo_actual` del cliente
- Se valida que el cliente tenga crédito disponible antes de permitir el pago a fiado

---

## Ejemplos con cURL

### Crear Factura Mixta
```bash
curl -X POST http://localhost:8000/api/facturacion/facturas/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "descuento": 0,
    "observaciones": "Venta mixta",
    "detalles": [
      {
        "producto_id": 1,
        "producto_empresa": "FERRETERIA",
        "cantidad": 10,
        "precio_unitario": 50.00
      },
      {
        "producto_id": 5,
        "producto_empresa": "BLOQUERA",
        "cantidad": 100,
        "precio_unitario": 5.00
      },
      {
        "producto_id": 3,
        "producto_empresa": "PIEDRINERA",
        "cantidad": 25.5,
        "precio_unitario": 100.00
      }
    ]
  }'
```

### Agregar Pagos Múltiples
```bash
curl -X POST http://localhost:8000/api/facturacion/facturas/1/agregar_pagos_multiples/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "pagos": [
      {
        "tipo_pago": "EFECTIVO",
        "monto": 1000.00
      },
      {
        "tipo_pago": "TARJETA",
        "monto": 500.00,
        "referencia": "****1234"
      },
      {
        "tipo_pago": "FIADO",
        "monto": 1450.00
      }
    ]
  }'
```

---

## Ejemplos con JavaScript (Fetch)

### Crear Factura Mixta
```javascript
const crearFacturaMixta = async (clienteId, detalles) => {
  const response = await fetch('http://localhost:8000/api/facturacion/facturas/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      cliente: clienteId,
      detalles: detalles
    })
  });
  
  return await response.json();
};

// Ejemplo de uso
const detalles = [
  {
    producto_id: 1,
    producto_empresa: 'FERRETERIA',
    cantidad: 10,
    precio_unitario: 50.00
  },
  {
    producto_id: 5,
    producto_empresa: 'BLOQUERA',
    cantidad: 100,
    precio_unitario: 5.00
  },
  {
    producto_id: 3,
    producto_empresa: 'PIEDRINERA',
    cantidad: 25.5,
    precio_unitario: 100.00
  }
];

crearFacturaMixta(1, detalles);
```

### Agregar Pagos Múltiples
```javascript
const agregarPagosMultiples = async (facturaId, pagos) => {
  const response = await fetch(
    `http://localhost:8000/api/facturacion/facturas/${facturaId}/agregar_pagos_multiples/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ pagos })
    }
  );
  
  return await response.json();
};

// Ejemplo de uso
agregarPagosMultiples(1, [
  { tipo_pago: 'EFECTIVO', monto: 1000.00 },
  { tipo_pago: 'TARJETA', monto: 500.00, referencia: '****1234' },
  { tipo_pago: 'FIADO', monto: 1450.00 }
]);
```

---

## Notas Importantes

1. **Facturas Mixtas**: El sistema detecta automáticamente cuando hay productos de múltiples empresas y asigna el prefijo "MIXT" al número de factura.

2. **Números de Factura**:
   - Ferretería: FERR000001, FERR000002, ...
   - Bloquera: BLOQ000001, BLOQ000002, ...
   - Piedrinera: PIED000001, PIED000002, ...
   - Mixta: MIXT000001, MIXT000002, ...

3. **Stock**: Se valida y actualiza automáticamente al crear la factura.

4. **Precios**: Si no se proporciona `precio_unitario`, se usa el precio del producto en el momento de la venta.

5. **Fiado**: Se valida automáticamente el crédito disponible del cliente antes de permitir pagos a fiado.

6. **Anulación**: Solo se puede anular si no tiene pagos registrados. Al anular, se revierte el stock.

---

## Resumen de Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/facturas/` | GET | Listar facturas |
| `/facturas/` | POST | Crear factura (puede incluir productos de las 3 empresas) |
| `/facturas/{id}/` | GET | Obtener detalle de factura |
| `/facturas/{id}/agregar_pago/` | POST | Agregar un pago |
| `/facturas/{id}/agregar_pagos_multiples/` | POST | Agregar múltiples pagos |
| `/facturas/{id}/anular/` | POST | Anular factura |
| `/facturas/estadisticas/` | GET | Estadísticas de facturación |
| `/pagos/` | GET | Listar pagos |
| `/pagos/{id}/` | GET | Obtener detalle de pago |

Todos los endpoints requieren autenticación mediante JWT.

