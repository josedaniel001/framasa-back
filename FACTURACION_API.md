# Documentación API de Facturación - Frontend

Documentación completa de la API de facturación unificada para integración con el frontend.

## Base URL
```
http://localhost:8000/api/facturacion/
```

## Autenticación
Todos los endpoints requieren autenticación JWT:
```
Authorization: Bearer {token}
```

---

## 1. Crear Factura

### Endpoint
```
POST /api/facturacion/facturas/
```

### Request Body
```typescript
interface FacturaCreateRequest {
  cliente: number;                    // ID del cliente (requerido)
  empresa?: string;                    // Opcional: FERRETERIA, BLOQUERA, PIEDRINERA, MIXTA
  descuento?: number;                  // Descuento general (default: 0)
  observaciones?: string;               // Observaciones adicionales
  fecha_vencimiento?: string;          // YYYY-MM-DD (para crédito)
  detalles: DetalleFacturaRequest[];    // Array de productos (requerido)
}

interface DetalleFacturaRequest {
  producto_id: number;                 // ID del producto (requerido)
  producto_empresa: string;            // FERRETERIA | BLOQUERA | PIEDRINERA (requerido)
  cantidad: number;                    // Cantidad (decimal para piedrinera, entero para otros)
  precio_unitario?: number;            // Opcional: si no se envía, usa precio del producto
  descuento?: number;                  // Descuento del detalle (default: 0)
}
```

### Ejemplo Request
```json
{
  "cliente": 1,
  "descuento": 50.00,
  "observaciones": "Venta mixta",
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

### Response (201 Created)
```typescript
interface FacturaResponse {
  id: number;
  numero_factura: string;              // Ej: "MIXT000001"
  empresa: string;                     // FERRETERIA | BLOQUERA | PIEDRINERA | MIXTA
  empresa_display: string;             // "Ferretería" | "Bloquera" | "Piedrinera" | "Mixta (Múltiples Empresas)"
  cliente: number;
  cliente_id: number;
  cliente_nombre: string;
  cliente_nit: string | null;
  subtotal: number;
  descuento: number;
  total: number;
  total_pagado: number;
  saldo_pendiente: number;
  estado: string;                       // BORRADOR | PENDIENTE | PARCIAL | PAGADA | ANULADA
  estado_display: string;
  observaciones: string | null;
  usuario: number;
  usuario_id: number;
  usuario_nombre: string;
  fecha_factura: string;               // ISO 8601
  fecha_vencimiento: string | null;    // YYYY-MM-DD
  detalles: DetalleFacturaResponse[];
  pagos: PagoResponse[];
  created_at: string;
  updated_at: string;
}

interface DetalleFacturaResponse {
  id: number;
  factura: number;
  producto_id: number;
  producto_empresa: string;
  producto_codigo: string;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
  descuento: number;
  subtotal: number;
  created_at: string;
  updated_at: string;
}
```

### Ejemplo Response
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
  "observaciones": "Venta mixta",
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
      "subtotal": 500.00,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
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
      "subtotal": 500.00,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
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
      "subtotal": 2550.00,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
    }
  ],
  "pagos": [],
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

### Errores Posibles

#### Stock Insuficiente (400)
```json
{
  "detalles": [
    {
      "cantidad": ["Stock insuficiente. Stock disponible: 5"]
    }
  ]
}
```

#### Producto No Encontrado (400)
```json
{
  "detalles": [
    {
      "producto_id": ["Producto no encontrado o inactivo"]
    }
  ]
}
```

---

## 2. Listar Facturas

### Endpoint
```
GET /api/facturacion/facturas/
```

### Query Parameters (Opcionales)
- `cliente`: ID del cliente (número)
- `empresa`: FERRETERIA | BLOQUERA | PIEDRINERA | MIXTA
- `estado`: BORRADOR | PENDIENTE | PARCIAL | PAGADA | ANULADA
- `fecha_desde`: YYYY-MM-DD
- `fecha_hasta`: YYYY-MM-DD
- `numero`: Búsqueda parcial por número de factura
- `page`: Número de página (paginación)

### Ejemplo Request
```http
GET /api/facturacion/facturas/?empresa=MIXTA&estado=PENDIENTE&fecha_desde=2025-01-01&page=1
```

### Response (200 OK)
```typescript
interface FacturaListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: FacturaResponse[];
}
```

### Ejemplo Response
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/facturacion/facturas/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero_factura": "MIXT000001",
      "empresa": "MIXTA",
      "cliente_nombre": "Juan Pérez",
      "total": 2950.00,
      "total_pagado": 0.00,
      "saldo_pendiente": 2950.00,
      "estado": "PENDIENTE",
      "fecha_factura": "2025-01-20T10:30:00Z",
      ...
    }
  ]
}
```

---

## 3. Obtener Detalle de Factura

### Endpoint
```
GET /api/facturacion/facturas/{id}/
```

### Response (200 OK)
Retorna un objeto `FacturaResponse` completo con todos los detalles y pagos.

---

## 4. Agregar Pagos Múltiples

### Endpoint
```
POST /api/facturacion/facturas/{id}/agregar_pagos_multiples/
```

### Request Body
```typescript
interface PagosMultiplesRequest {
  pagos: PagoRequest[];
}

interface PagoRequest {
  tipo_pago: string;                    // EFECTIVO | TARJETA | FIADO
  monto: number;                       // Monto del pago (requerido)
  referencia?: string;                 // Número de tarjeta, referencia, etc.
  observaciones?: string;              // Observaciones del pago
}
```

### Ejemplo Request
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

### Response (201 Created)
```typescript
interface PagosMultiplesResponse {
  factura: FacturaResponse;
  pagos_creados: PagoResponse[];
}

interface PagoResponse {
  id: number;
  factura: number;
  factura_id: number;
  tipo_pago: string;
  tipo_pago_display: string;           // "Efectivo" | "Tarjeta" | "Fiado"
  monto: number;
  referencia: string | null;
  observaciones: string | null;
  usuario: number;
  usuario_id: number;
  usuario_nombre: string;
  fecha_pago: string;                  // ISO 8601
  created_at: string;
  updated_at: string;
}
```

### Ejemplo Response
```json
{
  "factura": {
    "id": 1,
    "numero_factura": "MIXT000001",
    "total": 2950.00,
    "total_pagado": 2950.00,
    "saldo_pendiente": 0.00,
    "estado": "PAGADA",
    "estado_display": "Pagada",
    ...
  },
  "pagos_creados": [
    {
      "id": 1,
      "factura": 1,
      "factura_id": 1,
      "tipo_pago": "EFECTIVO",
      "tipo_pago_display": "Efectivo",
      "monto": 1000.00,
      "referencia": null,
      "observaciones": "Pago en efectivo",
      "usuario": 1,
      "usuario_id": 1,
      "usuario_nombre": "admin",
      "fecha_pago": "2025-01-20T11:00:00Z",
      "created_at": "2025-01-20T11:00:00Z",
      "updated_at": "2025-01-20T11:00:00Z"
    },
    {
      "id": 2,
      "factura": 1,
      "factura_id": 1,
      "tipo_pago": "TARJETA",
      "tipo_pago_display": "Tarjeta",
      "monto": 500.00,
      "referencia": "****1234",
      "observaciones": "Pago con tarjeta de crédito",
      "usuario": 1,
      "usuario_id": 1,
      "usuario_nombre": "admin",
      "fecha_pago": "2025-01-20T11:00:00Z",
      "created_at": "2025-01-20T11:00:00Z",
      "updated_at": "2025-01-20T11:00:00Z"
    },
    {
      "id": 3,
      "factura": 1,
      "factura_id": 1,
      "tipo_pago": "FIADO",
      "tipo_pago_display": "Fiado",
      "monto": 1450.00,
      "referencia": null,
      "observaciones": "Resto a crédito",
      "usuario": 1,
      "usuario_id": 1,
      "usuario_nombre": "admin",
      "fecha_pago": "2025-01-20T11:00:00Z",
      "created_at": "2025-01-20T11:00:00Z",
      "updated_at": "2025-01-20T11:00:00Z"
    }
  ]
}
```

### Errores Posibles

#### Monto Excede Saldo (400)
```json
{
  "error": "El total de pagos (3000.00) excede el saldo pendiente (2950.00)"
}
```

#### Crédito Insuficiente para Fiado (400)
```json
{
  "error": "Error en pago a fiado: Crédito insuficiente. Disponible: Q500.00"
}
```

#### Cliente No Permite Fiado (400)
```json
{
  "error": "Error en pago a fiado: El cliente no tiene permitido el fiado"
}
```

---

## 5. Agregar un Pago Individual

### Endpoint
```
POST /api/facturacion/facturas/{id}/agregar_pago/
```

### Request Body
```json
{
  "tipo_pago": "EFECTIVO",
  "monto": 500.00,
  "referencia": "",
  "observaciones": "Pago parcial"
}
```

### Response (201 Created)
Retorna un objeto `PagoResponse`.

---

## 6. Anular Factura

### Endpoint
```
POST /api/facturacion/facturas/{id}/anular/
```

### Response (200 OK)
Retorna el objeto `FacturaResponse` con `estado: "ANULADA"`.

### Errores Posibles

#### Factura Ya Anulada (400)
```json
{
  "error": "La factura ya está anulada"
}
```

#### Factura con Pagos (400)
```json
{
  "error": "No se puede anular una factura con pagos registrados"
}
```

---

## 7. Estadísticas de Facturación

### Endpoint
```
GET /api/facturacion/facturas/estadisticas/
```

### Query Parameters (Opcionales)
- `fecha_desde`: YYYY-MM-DD
- `fecha_hasta`: YYYY-MM-DD

### Response (200 OK)
```typescript
interface EstadisticasResponse {
  total_facturas: number;
  total_ventas: number;
  total_pagado: number;
  total_pendiente: number;
  por_estado: Array<{
    estado: string;
    count: number;
    total: number;
  }>;
  por_empresa: Array<{
    empresa: string;
    count: number;
    total: number;
  }>;
}
```

### Ejemplo Response
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
    },
    {
      "estado": "PARCIAL",
      "count": 20,
      "total": 20000.50
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
    },
    {
      "empresa": "BLOQUERA",
      "count": 30,
      "total": 50000.00
    },
    {
      "empresa": "PIEDRINERA",
      "count": 10,
      "total": 20000.50
    }
  ]
}
```

---

## 8. Listar Pagos

### Endpoint
```
GET /api/facturacion/pagos/
```

### Query Parameters (Opcionales)
- `factura`: ID de la factura
- `tipo_pago`: EFECTIVO | TARJETA | FIADO
- `fecha_desde`: YYYY-MM-DD
- `fecha_hasta`: YYYY-MM-DD
- `page`: Número de página

### Response (200 OK)
Retorna una lista paginada de `PagoResponse[]`.

---

## 9. Obtener Detalle de Pago

### Endpoint
```
GET /api/facturacion/pagos/{id}/
```

### Response (200 OK)
Retorna un objeto `PagoResponse`.

---

## Constantes y Enums

### Estados de Factura
```typescript
enum EstadoFactura {
  BORRADOR = 'BORRADOR',
  PENDIENTE = 'PENDIENTE',
  PARCIAL = 'PARCIAL',
  PAGADA = 'PAGADA',
  ANULADA = 'ANULADA'
}
```

### Tipos de Pago
```typescript
enum TipoPago {
  EFECTIVO = 'EFECTIVO',
  TARJETA = 'TARJETA',
  FIADO = 'FIADO'
}
```

### Empresas
```typescript
enum EmpresaFactura {
  FERRETERIA = 'FERRETERIA',
  BLOQUERA = 'BLOQUERA',
  PIEDRINERA = 'PIEDRINERA',
  MIXTA = 'MIXTA'
}
```

---

## Ejemplos de Código Frontend

### TypeScript/React - Crear Factura Mixta
```typescript
interface FacturaCreateRequest {
  cliente: number;
  descuento?: number;
  observaciones?: string;
  fecha_vencimiento?: string;
  detalles: Array<{
    producto_id: number;
    producto_empresa: 'FERRETERIA' | 'BLOQUERA' | 'PIEDRINERA';
    cantidad: number;
    precio_unitario?: number;
    descuento?: number;
  }>;
}

const crearFactura = async (
  request: FacturaCreateRequest,
  token: string
): Promise<FacturaResponse> => {
  const response = await fetch('http://localhost:8000/api/facturacion/facturas/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || JSON.stringify(error));
  }
  
  return await response.json();
};

// Ejemplo de uso
const facturaMixta: FacturaCreateRequest = {
  cliente: 1,
  descuento: 50.00,
  observaciones: 'Venta mixta',
  detalles: [
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
  ]
};

try {
  const factura = await crearFactura(facturaMixta, token);
  console.log('Factura creada:', factura.numero_factura);
} catch (error) {
  console.error('Error al crear factura:', error);
}
```

### TypeScript/React - Agregar Pagos Múltiples
```typescript
interface PagoRequest {
  tipo_pago: 'EFECTIVO' | 'TARJETA' | 'FIADO';
  monto: number;
  referencia?: string;
  observaciones?: string;
}

const agregarPagosMultiples = async (
  facturaId: number,
  pagos: PagoRequest[],
  token: string
) => {
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
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || JSON.stringify(error));
  }
  
  return await response.json();
};

// Ejemplo de uso
const pagos: PagoRequest[] = [
  {
    tipo_pago: 'EFECTIVO',
    monto: 1000.00,
    observaciones: 'Pago en efectivo'
  },
  {
    tipo_pago: 'TARJETA',
    monto: 500.00,
    referencia: '****1234',
    observaciones: 'Pago con tarjeta'
  },
  {
    tipo_pago: 'FIADO',
    monto: 1450.00,
    observaciones: 'Resto a crédito'
  }
];

try {
  const resultado = await agregarPagosMultiples(1, pagos, token);
  console.log('Factura pagada:', resultado.factura.estado);
  console.log('Pagos creados:', resultado.pagos_creados.length);
} catch (error) {
  console.error('Error al agregar pagos:', error);
}
```

### TypeScript/React - Listar Facturas con Filtros
```typescript
interface FacturaFilters {
  cliente?: number;
  empresa?: 'FERRETERIA' | 'BLOQUERA' | 'PIEDRINERA' | 'MIXTA';
  estado?: 'BORRADOR' | 'PENDIENTE' | 'PARCIAL' | 'PAGADA' | 'ANULADA';
  fecha_desde?: string;  // YYYY-MM-DD
  fecha_hasta?: string;  // YYYY-MM-DD
  numero?: string;
  page?: number;
}

const listarFacturas = async (
  filters: FacturaFilters = {},
  token: string
) => {
  const params = new URLSearchParams();
  
  if (filters.cliente) params.append('cliente', filters.cliente.toString());
  if (filters.empresa) params.append('empresa', filters.empresa);
  if (filters.estado) params.append('estado', filters.estado);
  if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
  if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);
  if (filters.numero) params.append('numero', filters.numero);
  if (filters.page) params.append('page', filters.page.toString());
  
  const response = await fetch(
    `http://localhost:8000/api/facturacion/facturas/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Error al listar facturas');
  }
  
  return await response.json();
};

// Ejemplo de uso
const facturas = await listarFacturas({
  empresa: 'MIXTA',
  estado: 'PENDIENTE',
  fecha_desde: '2025-01-01',
  page: 1
}, token);
```

### TypeScript/React - Hook Personalizado (React)
```typescript
import { useState, useEffect } from 'react';

interface UseFacturaProps {
  facturaId?: number;
  token: string;
}

export const useFactura = ({ facturaId, token }: UseFacturaProps) => {
  const [factura, setFactura] = useState<FacturaResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const cargarFactura = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:8000/api/facturacion/facturas/${id}/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Error al cargar factura');
      }
      
      const data = await response.json();
      setFactura(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (facturaId) {
      cargarFactura(facturaId);
    }
  }, [facturaId, token]);
  
  return { factura, loading, error, recargar: () => facturaId && cargarFactura(facturaId) };
};
```

---

## Validaciones Importantes

### Al Crear Factura
1. **Stock**: Se valida que haya stock suficiente antes de crear la factura
2. **Productos Activos**: Solo se pueden facturar productos activos
3. **Cantidades**: 
   - Ferretería y Bloquera: números enteros
   - Piedrinera: números decimales (m³)

### Al Agregar Pagos
1. **Saldo Pendiente**: La suma de pagos no puede exceder el saldo pendiente
2. **Fiado**: 
   - El cliente debe tener `permite_fiado = true`
   - El monto a fiado no puede exceder el crédito disponible
   - Se calcula: `credito_disponible = limite_credito - saldo_actual`

### Al Anular Factura
1. Solo se puede anular si `total_pagado = 0`
2. Al anular, se revierte el stock de todos los productos

---

## Flujo Recomendado para Frontend

### 1. Crear Factura
```
1. Usuario selecciona cliente
2. Usuario agrega productos (pueden ser de diferentes empresas)
3. Frontend valida:
   - Cliente seleccionado
   - Al menos un producto
   - Stock disponible (opcional, el backend también valida)
4. Enviar POST /api/facturacion/facturas/
5. Mostrar factura creada con número y totales
```

### 2. Agregar Pagos
```
1. Mostrar factura con saldo pendiente
2. Usuario ingresa pagos:
   - Efectivo: monto
   - Tarjeta: monto + referencia
   - Fiado: monto (validar crédito disponible)
3. Frontend valida:
   - Suma de pagos <= saldo pendiente
   - Si hay fiado, verificar crédito disponible del cliente
4. Enviar POST /api/facturacion/facturas/{id}/agregar_pagos_multiples/
5. Actualizar estado de factura (PAGADA si saldo = 0)
```

### 3. Visualizar Factura
```
1. Cargar GET /api/facturacion/facturas/{id}/
2. Mostrar:
   - Información de factura
   - Lista de detalles (productos)
   - Lista de pagos
   - Totales y saldos
```

---

## Notas para el Frontend

1. **Números de Factura**: Se generan automáticamente, no es necesario enviarlos
2. **Empresa Mixta**: Si incluyes productos de múltiples empresas, el sistema automáticamente usa `empresa: "MIXTA"` y prefijo "MIXT"
3. **Precios**: Si no envías `precio_unitario`, se usa el precio actual del producto
4. **Stock**: Se actualiza automáticamente al crear la factura
5. **Totales**: Se calculan automáticamente, no es necesario enviarlos
6. **Moneda**: Todos los montos están en Quetzales (GTQ) [[memory:7529943]]

---

## Endpoints Resumen

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/facturas/` | Crear factura (puede incluir productos de las 3 empresas) |
| GET | `/facturas/` | Listar facturas con filtros |
| GET | `/facturas/{id}/` | Obtener detalle de factura |
| POST | `/facturas/{id}/agregar_pago/` | Agregar un pago |
| POST | `/facturas/{id}/agregar_pagos_multiples/` | Agregar múltiples pagos |
| POST | `/facturas/{id}/anular/` | Anular factura |
| GET | `/facturas/estadisticas/` | Estadísticas de facturación |
| GET | `/pagos/` | Listar pagos |
| GET | `/pagos/{id}/` | Obtener detalle de pago |

Todos los endpoints requieren autenticación JWT.

---

## 10. Crear Cotización

### Endpoint
```
POST /api/facturacion/cotizaciones/
```

### Request Body
```typescript
interface CotizacionCreateRequest {
  cliente: number;                    // ID del cliente (requerido)
  empresa?: string;                    // Opcional: FERRETERIA, BLOQUERA, PIEDRINERA, MIXTA
  descuento?: number;                  // Descuento general (default: 0)
  observaciones?: string;               // Observaciones adicionales
  condiciones?: string;                 // Términos y condiciones de la cotización
  fecha_vencimiento: string;            // YYYY-MM-DD (requerido) - Fecha hasta la cual es válida
  detalles: DetalleCotizacionRequest[]; // Array de productos (requerido)
}

interface DetalleCotizacionRequest {
  producto_id: number;                 // ID del producto (requerido)
  producto_empresa: string;            // FERRETERIA | BLOQUERA | PIEDRINERA (requerido)
  cantidad: number;                    // Cantidad (decimal para piedrinera, entero para otros)
  precio_unitario?: number;            // Opcional: si no se envía, usa precio del producto
  descuento?: number;                  // Descuento del detalle (default: 0)
}
```

### Ejemplo Request
```json
{
  "cliente": 1,
  "empresa": "FERRETERIA",
  "descuento": 0,
  "fecha_vencimiento": "2025-02-15",
  "observaciones": "Cotización para cliente VIP",
  "condiciones": "Válida por 30 días. Precios sujetos a cambio sin previo aviso.",
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
    }
  ]
}
```

### Response (201 Created)
```typescript
interface CotizacionResponse {
  id: number;
  numero_cotizacion: string;           // Ej: "COTF000001"
  empresa: string;                     // FERRETERIA | BLOQUERA | PIEDRINERA | MIXTA
  empresa_display: string;
  cliente: number;
  cliente_id: number;
  cliente_nombre: string;
  cliente_nit: string | null;
  subtotal: number;
  descuento: number;
  total: number;
  estado: string;                     // BORRADOR | ENVIADA | ACEPTADA | RECHAZADA | VENCIDA
  estado_display: string;
  observaciones: string | null;
  condiciones: string | null;
  fecha_vencimiento: string;           // YYYY-MM-DD
  fecha_aceptacion: string | null;     // ISO 8601 (solo si está aceptada)
  fecha_cotizacion: string;           // ISO 8601
  factura_generada: number | null;     // ID de factura si ya fue convertida
  factura_generada_numero: string | null; // Número de factura generada
  usuario: number;
  usuario_id: number;
  usuario_nombre: string;
  detalles: DetalleCotizacionResponse[];
  created_at: string;
  updated_at: string;
}

interface DetalleCotizacionResponse {
  id: number;
  cotizacion: number;
  producto_id: number;
  producto_empresa: string;
  producto_codigo: string;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
  descuento: number;
  subtotal: number;
  created_at: string;
  updated_at: string;
}
```

### Ejemplo Response
```json
{
  "id": 1,
  "numero_cotizacion": "COTF000001",
  "empresa": "FERRETERIA",
  "empresa_display": "Ferretería",
  "cliente": 1,
  "cliente_id": 1,
  "cliente_nombre": "Juan Pérez",
  "cliente_nit": "12345678-9",
  "subtotal": 1000.00,
  "descuento": 0,
  "total": 1000.00,
  "estado": "BORRADOR",
  "estado_display": "Borrador",
  "observaciones": "Cotización para cliente VIP",
  "condiciones": "Válida por 30 días. Precios sujetos a cambio sin previo aviso.",
  "fecha_vencimiento": "2025-02-15",
  "fecha_aceptacion": null,
  "fecha_cotizacion": "2025-01-20T10:30:00Z",
  "factura_generada": null,
  "factura_generada_numero": null,
  "usuario": 1,
  "usuario_id": 1,
  "usuario_nombre": "admin",
  "detalles": [
    {
      "id": 1,
      "cotizacion": 1,
      "producto_id": 1,
      "producto_empresa": "FERRETERIA",
      "producto_codigo": "PROD001",
      "producto_nombre": "Martillo",
      "cantidad": 10,
      "precio_unitario": 50.00,
      "descuento": 0,
      "subtotal": 500.00,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
    },
    {
      "id": 2,
      "cotizacion": 1,
      "producto_id": 5,
      "producto_empresa": "BLOQUERA",
      "producto_codigo": "BLOQ005",
      "producto_nombre": "Bloque 15x20x40",
      "cantidad": 100,
      "precio_unitario": 5.00,
      "descuento": 0,
      "subtotal": 500.00,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
    }
  ],
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

---

## 11. Listar Cotizaciones

### Endpoint
```
GET /api/facturacion/cotizaciones/
```

### Query Parameters (Opcionales)
- `cliente`: ID del cliente (número)
- `empresa`: FERRETERIA | BLOQUERA | PIEDRINERA | MIXTA
- `estado`: BORRADOR | ENVIADA | ACEPTADA | RECHAZADA | VENCIDA
- `fecha_desde`: YYYY-MM-DD
- `fecha_hasta`: YYYY-MM-DD
- `numero`: Búsqueda parcial por número de cotización
- `vencidas`: true | false (filtrar solo cotizaciones vencidas)
- `page`: Número de página (paginación)

### Ejemplo Request
```http
GET /api/facturacion/cotizaciones/?estado=ENVIADA&fecha_desde=2025-01-01&page=1
```

### Response (200 OK)
Retorna una lista paginada de `CotizacionResponse[]`.

---

## 12. Obtener Detalle de Cotización

### Endpoint
```
GET /api/facturacion/cotizaciones/{id}/
```

### Response (200 OK)
Retorna un objeto `CotizacionResponse` completo con todos los detalles.

---

## 13. Enviar Cotización al Cliente

### Endpoint
```
POST /api/facturacion/cotizaciones/{id}/enviar/
```

### Descripción
Cambia el estado de la cotización de `BORRADOR` a `ENVIADA`, indicando que ha sido enviada al cliente.

### Response (200 OK)
Retorna el objeto `CotizacionResponse` con `estado: "ENVIADA"`.

### Errores Posibles

#### Solo Borradores (400)
```json
{
  "error": "Solo se pueden enviar cotizaciones en estado borrador"
}
```

---

## 14. Aceptar Cotización

### Endpoint
```
POST /api/facturacion/cotizaciones/{id}/aceptar/
```

### Descripción
Marca la cotización como aceptada por el cliente. Solo se puede aceptar si no está vencida.

### Response (200 OK)
Retorna el objeto `CotizacionResponse` con:
- `estado: "ACEPTADA"`
- `fecha_aceptacion`: Fecha y hora actual

### Errores Posibles

#### Ya Aceptada (400)
```json
{
  "error": "La cotización ya está aceptada"
}
```

#### Cotización Vencida (400)
```json
{
  "error": "La cotización está vencida y no puede ser aceptada"
}
```

---

## 15. Rechazar Cotización

### Endpoint
```
POST /api/facturacion/cotizaciones/{id}/rechazar/
```

### Descripción
Marca la cotización como rechazada por el cliente.

### Response (200 OK)
Retorna el objeto `CotizacionResponse` con `estado: "RECHAZADA"`.

### Errores Posibles

#### Ya Rechazada (400)
```json
{
  "error": "La cotización ya está rechazada"
}
```

#### Tiene Factura Generada (400)
```json
{
  "error": "No se puede rechazar una cotización que ya tiene una factura generada"
}
```

---

## 16. Convertir Cotización a Factura

### Endpoint
```
POST /api/facturacion/cotizaciones/{id}/convertir_a_factura/
```

### Descripción
Convierte una cotización aceptada en una factura. Este proceso:
1. Valida que la cotización esté aceptada y no vencida
2. Verifica que todos los productos tengan stock suficiente
3. Crea la factura con número automático
4. Crea los detalles de factura desde los detalles de cotización
5. Actualiza el inventario (crea movimientos de salida)
6. Vincula la factura generada a la cotización

### Response (201 Created)
```typescript
interface ConvertirCotizacionResponse {
  cotizacion: CotizacionResponse;
  factura: FacturaResponse;
  mensaje: string;
}
```

### Ejemplo Response
```json
{
  "cotizacion": {
    "id": 1,
    "numero_cotizacion": "COTF000001",
    "estado": "ACEPTADA",
    "factura_generada": 5,
    "factura_generada_numero": "FERR000001",
    ...
  },
  "factura": {
    "id": 5,
    "numero_factura": "FERR000001",
    "cliente_nombre": "Juan Pérez",
    "total": 1000.00,
    "estado": "PENDIENTE",
    "observaciones": "Generada desde cotización COTF000001",
    ...
  },
  "mensaje": "Cotización COTF000001 convertida exitosamente a factura FERR000001"
}
```

### Errores Posibles

#### No Aceptada (400)
```json
{
  "error": "La cotización debe estar aceptada para convertirla en factura"
}
```

#### Ya Tiene Factura (400)
```json
{
  "error": "Esta cotización ya tiene una factura generada"
}
```

#### Vencida (400)
```json
{
  "error": "La cotización está vencida"
}
```

#### Stock Insuficiente (400)
```json
{
  "error": "Stock insuficiente para Martillo. Disponible: 5"
}
```

#### Producto No Encontrado (400)
```json
{
  "error": "Producto Martillo no encontrado o inactivo"
}
```

---

## Estados de Cotización

```typescript
enum EstadoCotizacion {
  BORRADOR = 'BORRADOR',        // Recién creada, en edición
  ENVIADA = 'ENVIADA',          // Enviada al cliente
  ACEPTADA = 'ACEPTADA',        // Cliente aceptó la cotización
  RECHAZADA = 'RECHAZADA',      // Cliente rechazó la cotización
  VENCIDA = 'VENCIDA'           // Pasó la fecha de vencimiento
}
```

---

## Ejemplos de Código Frontend - Cotizaciones

### TypeScript/React - Crear Cotización
```typescript
interface CotizacionCreateRequest {
  cliente: number;
  empresa?: string;
  descuento?: number;
  observaciones?: string;
  condiciones?: string;
  fecha_vencimiento: string;  // YYYY-MM-DD
  detalles: Array<{
    producto_id: number;
    producto_empresa: 'FERRETERIA' | 'BLOQUERA' | 'PIEDRINERA';
    cantidad: number;
    precio_unitario?: number;
    descuento?: number;
  }>;
}

const crearCotizacion = async (
  request: CotizacionCreateRequest,
  token: string
): Promise<CotizacionResponse> => {
  const response = await fetch('http://localhost:8000/api/facturacion/cotizaciones/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || JSON.stringify(error));
  }
  
  return await response.json();
};

// Ejemplo de uso
const cotizacion: CotizacionCreateRequest = {
  cliente: 1,
  empresa: 'FERRETERIA',
  descuento: 0,
  fecha_vencimiento: '2025-02-15',
  observaciones: 'Cotización para cliente VIP',
  condiciones: 'Válida por 30 días',
  detalles: [
    {
      producto_id: 1,
      producto_empresa: 'FERRETERIA',
      cantidad: 10,
      precio_unitario: 50.00
    }
  ]
};

try {
  const cotizacionCreada = await crearCotizacion(cotizacion, token);
  console.log('Cotización creada:', cotizacionCreada.numero_cotizacion);
} catch (error) {
  console.error('Error al crear cotización:', error);
}
```

### TypeScript/React - Aceptar y Convertir a Factura
```typescript
const aceptarCotizacion = async (
  cotizacionId: number,
  token: string
): Promise<CotizacionResponse> => {
  const response = await fetch(
    `http://localhost:8000/api/facturacion/cotizaciones/${cotizacionId}/aceptar/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || JSON.stringify(error));
  }
  
  return await response.json();
};

const convertirAFactura = async (
  cotizacionId: number,
  token: string
): Promise<ConvertirCotizacionResponse> => {
  const response = await fetch(
    `http://localhost:8000/api/facturacion/cotizaciones/${cotizacionId}/convertir_a_factura/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || JSON.stringify(error));
  }
  
  return await response.json();
};

// Ejemplo de uso - Flujo completo
try {
  // 1. Aceptar cotización
  const cotizacionAceptada = await aceptarCotizacion(1, token);
  console.log('Cotización aceptada:', cotizacionAceptada.numero_cotizacion);
  
  // 2. Convertir a factura
  const resultado = await convertirAFactura(1, token);
  console.log('Factura generada:', resultado.factura.numero_factura);
  console.log('Mensaje:', resultado.mensaje);
} catch (error) {
  console.error('Error en el proceso:', error);
}
```

### TypeScript/React - Listar Cotizaciones con Filtros
```typescript
interface CotizacionFilters {
  cliente?: number;
  empresa?: 'FERRETERIA' | 'BLOQUERA' | 'PIEDRINERA' | 'MIXTA';
  estado?: 'BORRADOR' | 'ENVIADA' | 'ACEPTADA' | 'RECHAZADA' | 'VENCIDA';
  fecha_desde?: string;  // YYYY-MM-DD
  fecha_hasta?: string;  // YYYY-MM-DD
  numero?: string;
  vencidas?: boolean;
  page?: number;
}

const listarCotizaciones = async (
  filters: CotizacionFilters = {},
  token: string
) => {
  const params = new URLSearchParams();
  
  if (filters.cliente) params.append('cliente', filters.cliente.toString());
  if (filters.empresa) params.append('empresa', filters.empresa);
  if (filters.estado) params.append('estado', filters.estado);
  if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
  if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);
  if (filters.numero) params.append('numero', filters.numero);
  if (filters.vencidas) params.append('vencidas', 'true');
  if (filters.page) params.append('page', filters.page.toString());
  
  const response = await fetch(
    `http://localhost:8000/api/facturacion/cotizaciones/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Error al listar cotizaciones');
  }
  
  return await response.json();
};

// Ejemplo de uso
const cotizaciones = await listarCotizaciones({
  estado: 'ENVIADA',
  fecha_desde: '2025-01-01',
  page: 1
}, token);
```

---

## Flujo Recomendado para Cotizaciones

### 1. Crear Cotización
```
1. Usuario selecciona cliente
2. Usuario agrega productos (pueden ser de diferentes empresas)
3. Usuario define fecha de vencimiento
4. Usuario puede agregar condiciones y observaciones
5. Enviar POST /api/facturacion/cotizaciones/
6. Mostrar cotización creada en estado BORRADOR
```

### 2. Enviar Cotización
```
1. Usuario revisa cotización en estado BORRADOR
2. Enviar POST /api/facturacion/cotizaciones/{id}/enviar/
3. Estado cambia a ENVIADA
4. Se puede enviar al cliente (email, PDF, etc.)
```

### 3. Cliente Acepta
```
1. Cliente acepta la cotización
2. Enviar POST /api/facturacion/cotizaciones/{id}/aceptar/
3. Estado cambia a ACEPTADA
4. Se registra fecha_aceptacion
```

### 4. Convertir a Factura
```
1. Usuario verifica que cotización esté ACEPTADA
2. Sistema valida:
   - No vencida
   - Stock disponible
   - No tiene factura generada
3. Enviar POST /api/facturacion/cotizaciones/{id}/convertir_a_factura/
4. Se crea factura automáticamente
5. Se actualiza inventario
6. Cotización queda vinculada a la factura
```

---

## Notas Importantes sobre Cotizaciones

1. **Números de Cotización**: Se generan automáticamente con prefijos:
   - `COTF` para Ferretería
   - `COTB` para Bloquera
   - `COTP` para Piedrinera
   - `COTM` para Mixta

2. **Fecha de Vencimiento**: Es obligatoria al crear la cotización

3. **Stock**: No se valida stock al crear la cotización, solo al convertir a factura

4. **Precios**: Se guardan al momento de la cotización (snapshot), pueden cambiar después

5. **Conversión**: Solo se puede convertir una vez. Una cotización convertida no puede volver a convertirse

6. **Estados**: El flujo típico es: BORRADOR → ENVIADA → ACEPTADA → (convertir a factura)

7. **Vencimiento**: Las cotizaciones vencidas no pueden ser aceptadas ni convertidas

---

## Endpoints Resumen - Cotizaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/cotizaciones/` | Crear cotización |
| GET | `/cotizaciones/` | Listar cotizaciones con filtros |
| GET | `/cotizaciones/{id}/` | Obtener detalle de cotización |
| PUT | `/cotizaciones/{id}/` | Actualizar cotización |
| PATCH | `/cotizaciones/{id}/` | Actualizar parcialmente cotización |
| DELETE | `/cotizaciones/{id}/` | Eliminar cotización |
| POST | `/cotizaciones/{id}/enviar/` | Enviar cotización al cliente |
| POST | `/cotizaciones/{id}/aceptar/` | Aceptar cotización |
| POST | `/cotizaciones/{id}/rechazar/` | Rechazar cotización |
| POST | `/cotizaciones/{id}/convertir_a_factura/` | Convertir cotización a factura |

Todos los endpoints requieren autenticación JWT.

