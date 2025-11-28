# Documentación API de Taller (Maquinaria) - Frontend

Documentación completa de la API de maquinaria para integración con el frontend.

## Base URL
```
http://localhost:8000/api/taller/
```

## Autenticación
Todos los endpoints requieren autenticación JWT:
```
Authorization: Bearer {token}
```

---

## 1. Listar Maquinaria

### Endpoint
```
GET /api/taller/maquinaria/
```

### Query Parameters (Opcionales)
- `search`: Búsqueda por código, nombre, marca o modelo
- `empresa`: Filtro por empresa (FERRETERIA, BLOQUERA, PIEDRINERA, CONSTRUCTORA, o 'todos')
- `tipo_maquinaria`: Filtro por tipo de maquinaria (ver tipos disponibles) o 'todos'
- `estado`: Filtro por estado actual o 'todos'
- `activo`: 'activo', 'inactivo' o 'todos'

### Ejemplo Request
```
GET /api/taller/maquinaria/?empresa=FERRETERIA&activo=activo&search=excavadora
```

### Response (200 OK)
```typescript
interface MaquinariaListResponse {
  id: string;
  codigo: string;
  nombre: string;
  empresa: string;                    // FERRETERIA | BLOQUERA | PIEDRINERA | CONSTRUCTORA
  empresaDisplay: string;              // "Ferretería" | "Bloquera" | "Piedrinera" | "Constructora"
  tipoMaquinaria: string;             // EXCAVADORA | RETROEXCAVADORA | etc.
  tipoMaquinariaDisplay: string;      // "Excavadora" | "Retroexcavadora" | etc.
  marca: string;
  modelo: string;
  estado: string;                     // Estado actual
  proximoMantenimiento: string | null; // YYYY-MM-DD
  seguroVigente: boolean;
  documentacionVigente: boolean;
  activo: boolean;
}
```

### Ejemplo Response
```json
[
  {
    "id": "1",
    "codigo": "EXC-001",
    "nombre": "Excavadora CAT 320",
    "empresa": "FERRETERIA",
    "empresaDisplay": "Ferretería",
    "tipoMaquinaria": "EXCAVADORA",
    "tipoMaquinariaDisplay": "Excavadora",
    "marca": "Caterpillar",
    "modelo": "320",
    "estado": "operativa",
    "proximoMantenimiento": "2025-02-15",
    "seguroVigente": true,
    "documentacionVigente": true,
    "activo": true
  }
]
```

---

## 2. Obtener Detalle de Maquinaria

### Endpoint
```
GET /api/taller/maquinaria/{id}/
```

### Response (200 OK)
```typescript
interface MaquinariaDetailResponse {
  id: string;
  codigo: string;
  nombre: string;
  empresa: string;
  empresaDisplay: string;
  tipoMaquinaria: string;
  tipoMaquinariaDisplay: string;
  marca: string;
  modelo: string;
  numeroSerie: string | null;
  añoFabricacion: number | null;
  estadoActual: string;
  fechaUltimoMantenimiento: string | null;  // YYYY-MM-DD
  fechaProximoMantenimiento: string | null;  // YYYY-MM-DD
  horasOperacion: number;
  kilometraje: number;
  seguroVigente: boolean;
  documentacionVigente: boolean;
  ubicacionActual: string | null;
  observaciones: string | null;
  activo: boolean;
  createdAt: string;                  // ISO 8601
  updatedAt: string;                   // ISO 8601
  // Campos en snake_case para compatibilidad
  empresa_display: string;
  tipo_maquinaria: string;
  tipo_maquinaria_display: string;
  estado_actual: string;
  fecha_ultimo_mantenimiento: string | null;
  fecha_proximo_mantenimiento: string | null;
  horas_operacion: number;
  seguro_vigente: boolean;
  documentacion_vigente: boolean;
  ubicacion_actual: string | null;
  created_at: string;
  updated_at: string;
}
```

### Ejemplo Response
```json
{
  "id": "1",
  "codigo": "EXC-001",
  "nombre": "Excavadora CAT 320",
  "empresa": "FERRETERIA",
  "empresaDisplay": "Ferretería",
  "tipoMaquinaria": "EXCAVADORA",
  "tipoMaquinariaDisplay": "Excavadora",
  "marca": "Caterpillar",
  "modelo": "320",
  "numeroSerie": "CAT320-2020-001",
  "añoFabricacion": 2020,
  "estadoActual": "operativa",
  "fechaUltimoMantenimiento": "2025-01-15",
  "fechaProximoMantenimiento": "2025-02-15",
  "horasOperacion": 2500,
  "kilometraje": 0,
  "seguroVigente": true,
  "documentacionVigente": true,
  "ubicacionActual": "Obra San Juan",
  "observaciones": "Requiere revisión de sistema hidráulico",
  "activo": true,
  "createdAt": "2025-01-01T10:00:00Z",
  "updatedAt": "2025-01-20T15:30:00Z",
  "empresa_display": "Ferretería",
  "tipo_maquinaria": "EXCAVADORA",
  "tipo_maquinaria_display": "Excavadora",
  "estado_actual": "operativa",
  "fecha_ultimo_mantenimiento": "2025-01-15",
  "fecha_proximo_mantenimiento": "2025-02-15",
  "horas_operacion": 2500,
  "seguro_vigente": true,
  "documentacion_vigente": true,
  "ubicacion_actual": "Obra San Juan",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-20T15:30:00Z"
}
```

---

## 3. Crear Maquinaria

### Endpoint
```
POST /api/taller/maquinaria/
```

### Request Body
```typescript
interface MaquinariaCreateRequest {
  codigo: string;                      // Código único (requerido)
  nombre: string;                       // Nombre o descripción (requerido)
  empresa: string;                      // FERRETERIA | BLOQUERA | PIEDRINERA | CONSTRUCTORA (requerido)
  tipo_maquinaria: string;             // Tipo de maquinaria (requerido)
  marca: string;                        // Marca (requerido)
  modelo: string;                       // Modelo (requerido)
  numero_serie?: string;                // Número de serie (opcional)
  año_fabricacion?: number;             // Año de fabricación (opcional, mínimo 1900)
  estado_actual: string;                // Estado actual (requerido)
  fecha_ultimo_mantenimiento?: string;  // YYYY-MM-DD (opcional)
  fecha_proximo_mantenimiento?: string; // YYYY-MM-DD (opcional)
  horas_operacion?: number;             // Horas de operación (default: 0)
  kilometraje?: number;                // Kilometraje (default: 0)
  seguro_vigente?: boolean;            // Seguro vigente (default: true)
  documentacion_vigente?: boolean;      // Documentación vigente (default: true)
  ubicacion_actual?: string;            // Ubicación actual (opcional)
  observaciones?: string;               // Observaciones (opcional)
  activo?: boolean;                     // Activo (default: true)
}
```

### Ejemplo Request
```json
{
  "codigo": "EXC-002",
  "nombre": "Excavadora Komatsu PC200",
  "empresa": "CONSTRUCTORA",
  "tipo_maquinaria": "EXCAVADORA",
  "marca": "Komatsu",
  "modelo": "PC200",
  "numero_serie": "KOM-PC200-2021-045",
  "año_fabricacion": 2021,
  "estado_actual": "operativa",
  "fecha_ultimo_mantenimiento": "2025-01-10",
  "fecha_proximo_mantenimiento": "2025-02-10",
  "horas_operacion": 1800,
  "kilometraje": 0,
  "seguro_vigente": true,
  "documentacion_vigente": true,
  "ubicacion_actual": "Obra Central",
  "observaciones": "Nueva adquisición",
  "activo": true
}
```

### Response (201 Created)
Retorna el objeto completo de maquinaria creada (mismo formato que GET /{id}/)

---

## 4. Actualizar Maquinaria

### Endpoint
```
PUT /api/taller/maquinaria/{id}/
PATCH /api/taller/maquinaria/{id}/
```

### Request Body
Mismo formato que crear, pero todos los campos son opcionales (excepto los que quieras actualizar).

### Ejemplo Request (PATCH)
```json
{
  "estado_actual": "en_mantenimiento",
  "fecha_ultimo_mantenimiento": "2025-01-25",
  "horas_operacion": 2600,
  "observaciones": "En mantenimiento preventivo"
}
```

### Response (200 OK)
Retorna el objeto completo de maquinaria actualizada.

---

## 5. Eliminar Maquinaria

### Endpoint
```
DELETE /api/taller/maquinaria/{id}/
```

### Response (204 No Content)
Sin contenido en el body.

---

## 6. Obtener Tipos de Maquinaria

### Endpoint
```
GET /api/taller/maquinaria/tipos/
```

### Response (200 OK)
```typescript
interface TipoMaquinariaResponse {
  value: string;
  label: string;
}
```

### Ejemplo Response
```json
[
  { "value": "EXCAVADORA", "label": "Excavadora" },
  { "value": "RETROEXCAVADORA", "label": "Retroexcavadora" },
  { "value": "CARGADOR", "label": "Cargador Frontal" },
  { "value": "COMPACTADORA", "label": "Compactadora" },
  { "value": "VIBRADOR", "label": "Vibrador de Concreto" },
  { "value": "MEZCLADORA", "label": "Mezcladora de Concreto" },
  { "value": "CORTADORA", "label": "Cortadora de Concreto" },
  { "value": "GENERADOR", "label": "Generador" },
  { "value": "COMPRESOR", "label": "Compresor de Aire" },
  { "value": "SOLDADORA", "label": "Soldadora" },
  { "value": "OTRO", "label": "Otro" }
]
```

---

## 7. Obtener Empresas Disponibles

### Endpoint
```
GET /api/taller/maquinaria/empresas/
```

### Response (200 OK)
```typescript
interface EmpresaResponse {
  value: string;
  label: string;
}
```

### Ejemplo Response
```json
[
  { "value": "FERRETERIA", "label": "Ferretería" },
  { "value": "BLOQUERA", "label": "Bloquera" },
  { "value": "PIEDRINERA", "label": "Piedrinera" },
  { "value": "CONSTRUCTORA", "label": "Constructora" }
]
```

---

## Tipos TypeScript Completos

```typescript
// Empresas
type EmpresaMaquinaria = 'FERRETERIA' | 'BLOQUERA' | 'PIEDRINERA' | 'CONSTRUCTORA';

// Tipos de Maquinaria
type TipoMaquinaria = 
  | 'EXCAVADORA'
  | 'RETROEXCAVADORA'
  | 'CARGADOR'
  | 'COMPACTADORA'
  | 'VIBRADOR'
  | 'MEZCLADORA'
  | 'CORTADORA'
  | 'GENERADOR'
  | 'COMPRESOR'
  | 'SOLDADORA'
  | 'OTRO';

// Estados comunes (pueden variar según necesidad)
type EstadoMaquinaria = 
  | 'operativa'
  | 'en_mantenimiento'
  | 'fuera_de_servicio'
  | 'reservada'
  | 'reparacion';

// Request para crear/actualizar
interface MaquinariaRequest {
  codigo: string;
  nombre: string;
  empresa: EmpresaMaquinaria;
  tipo_maquinaria: TipoMaquinaria;
  marca: string;
  modelo: string;
  numero_serie?: string;
  año_fabricacion?: number;
  estado_actual: string;
  fecha_ultimo_mantenimiento?: string;  // YYYY-MM-DD
  fecha_proximo_mantenimiento?: string;  // YYYY-MM-DD
  horas_operacion?: number;
  kilometraje?: number;
  seguro_vigente?: boolean;
  documentacion_vigente?: boolean;
  ubicacion_actual?: string;
  observaciones?: string;
  activo?: boolean;
}

// Response completo
interface MaquinariaResponse {
  id: string;
  codigo: string;
  nombre: string;
  empresa: EmpresaMaquinaria;
  empresaDisplay: string;
  tipoMaquinaria: TipoMaquinaria;
  tipoMaquinariaDisplay: string;
  marca: string;
  modelo: string;
  numeroSerie: string | null;
  añoFabricacion: number | null;
  estadoActual: string;
  fechaUltimoMantenimiento: string | null;
  fechaProximoMantenimiento: string | null;
  horasOperacion: number;
  kilometraje: number;
  seguroVigente: boolean;
  documentacionVigente: boolean;
  ubicacionActual: string | null;
  observaciones: string | null;
  activo: boolean;
  createdAt: string;
  updatedAt: string;
}
```

---

## Ejemplos de Uso

### Ejemplo 1: Listar maquinaria de una empresa específica
```typescript
const response = await fetch('/api/taller/maquinaria/?empresa=CONSTRUCTORA&activo=activo', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const maquinaria = await response.json();
```

### Ejemplo 2: Buscar maquinaria por texto
```typescript
const response = await fetch('/api/taller/maquinaria/?search=excavadora', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const resultados = await response.json();
```

### Ejemplo 3: Crear nueva maquinaria
```typescript
const nuevaMaquinaria = {
  codigo: 'RET-001',
  nombre: 'Retroexcavadora JCB 3CX',
  empresa: 'BLOQUERA',
  tipo_maquinaria: 'RETROEXCAVADORA',
  marca: 'JCB',
  modelo: '3CX',
  estado_actual: 'operativa',
  horas_operacion: 0,
  kilometraje: 0,
  seguro_vigente: true,
  documentacion_vigente: true,
  activo: true
};

const response = await fetch('/api/taller/maquinaria/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(nuevaMaquinaria)
});
const creada = await response.json();
```

### Ejemplo 4: Actualizar estado de maquinaria
```typescript
const actualizacion = {
  estado_actual: 'en_mantenimiento',
  fecha_ultimo_mantenimiento: '2025-01-25',
  horas_operacion: 3000
};

const response = await fetch(`/api/taller/maquinaria/${id}/`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(actualizacion)
});
const actualizada = await response.json();
```

### Ejemplo 5: Obtener tipos y empresas para formularios
```typescript
// Obtener tipos de maquinaria
const tiposResponse = await fetch('/api/taller/maquinaria/tipos/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const tipos = await tiposResponse.json();

// Obtener empresas
const empresasResponse = await fetch('/api/taller/maquinaria/empresas/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const empresas = await empresasResponse.json();
```

---

## Códigos de Estado HTTP

- `200 OK`: Solicitud exitosa (GET, PUT, PATCH)
- `201 Created`: Recurso creado exitosamente (POST)
- `204 No Content`: Recurso eliminado exitosamente (DELETE)
- `400 Bad Request`: Error en la validación de datos
- `401 Unauthorized`: Token de autenticación inválido o faltante
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

---

## Notas Importantes

1. **Camiones**: Los camiones se manejan en el módulo PIEDRINERA (`/api/piedrinera/camiones/`), no en el módulo de taller.

2. **Código único**: El campo `codigo` debe ser único en todo el sistema.

3. **Validaciones**:
   - `año_fabricacion` debe ser >= 1900
   - `horas_operacion` y `kilometraje` deben ser >= 0
   - `empresa` no puede ser MIXTA (solo empresas específicas)

4. **Filtros**: Todos los filtros en los query parameters son opcionales y se pueden combinar.

5. **Formato de fechas**: Las fechas se envían y reciben en formato `YYYY-MM-DD`.

6. **Paginación**: Actualmente no hay paginación implementada, se retornan todos los resultados. El frontend puede manejar la paginación si es necesario.

---

## Resumen de Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/maquinaria/` | Listar maquinaria (con filtros) |
| GET | `/maquinaria/{id}/` | Obtener detalle de maquinaria |
| POST | `/maquinaria/` | Crear nueva maquinaria |
| PUT | `/maquinaria/{id}/` | Actualizar maquinaria (completo) |
| PATCH | `/maquinaria/{id}/` | Actualizar maquinaria (parcial) |
| DELETE | `/maquinaria/{id}/` | Eliminar maquinaria |
| GET | `/maquinaria/tipos/` | Obtener tipos de maquinaria disponibles |
| GET | `/maquinaria/empresas/` | Obtener empresas disponibles |

