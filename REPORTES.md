# Documentación de Reportes

Este sistema proporciona reportes unificados y estadísticas predictivas para las tres empresas: Ferretería, Bloquera y Piedrinera.

## Base URL
```
http://localhost:8000/api/reportes/
```

---

## 1. Inventario Unificado

### Endpoint
```
GET /api/reportes/inventario_unificado/
```

### Descripción
Obtiene un reporte completo del inventario consolidado de las tres empresas, incluyendo estadísticas generales y desglose por empresa.

### Headers Requeridos
```
Authorization: Bearer {tu_token_jwt}
```

### Ejemplo de Request
```http
GET /api/reportes/inventario_unificado/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Respuesta (Ejemplo)
```json
{
  "resumen_general": {
    "total_productos": 150,
    "productos_activos": 140,
    "productos_inactivos": 10,
    "productos_stock_bajo": 25,
    "valor_inventario_total": 250000.50
  },
  "por_empresa": [
    {
      "empresa": "ferreteria",
      "total_productos": 80,
      "productos_activos": 75,
      "productos_inactivos": 5,
      "stock_total": 5000,
      "stock_minimo_total": 2000,
      "productos_stock_bajo": 15,
      "valor_inventario_estimado": 150000.00,
      "unidades": "unidades"
    },
    {
      "empresa": "bloquera",
      "total_productos": 40,
      "productos_activos": 38,
      "productos_inactivos": 2,
      "stock_total": 10000,
      "stock_minimo_total": 5000,
      "productos_stock_bajo": 8,
      "valor_inventario_estimado": 80000.00,
      "unidades": "unidades"
    },
    {
      "empresa": "piedrinera",
      "total_productos": 30,
      "productos_activos": 27,
      "productos_inactivos": 3,
      "stock_total": 500.5,
      "stock_minimo_total": 200.0,
      "productos_stock_bajo": 2,
      "valor_inventario_estimado": 20000.50,
      "unidades": "m³"
    }
  ],
  "total_general": {
    "total_productos": 150,
    "productos_activos": 140,
    "productos_inactivos": 10,
    "productos_stock_bajo": 25,
    "valor_inventario_total": 250000.50
  }
}
```

---

## 2. Top de Productos Más Vendidos

### Endpoint
```
GET /api/reportes/top_productos_vendidos/
```

### Descripción
Obtiene el ranking de los productos más vendidos, con opción de filtrar por empresa y rango de fechas.

### Parámetros de Filtro (Query Parameters - Opcionales)
- `empresa`: Empresa a filtrar (`ferreteria`, `bloquera`, `piedrinera`, `todas` - default: `todas`)
- `limit`: Número de productos a retornar (default: 10)
- `fecha_desde`: Fecha desde (formato: YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (formato: YYYY-MM-DD)

### Ejemplos de Requests

#### Top 10 de todas las empresas
```http
GET /api/reportes/top_productos_vendidos/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Top 5 de ferretería
```http
GET /api/reportes/top_productos_vendidos/?empresa=ferreteria&limit=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Top productos de bloquera en un rango de fechas
```http
GET /api/reportes/top_productos_vendidos/?empresa=bloquera&fecha_desde=2025-01-01&fecha_hasta=2025-01-31
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Respuesta (Ejemplo)
```json
[
  {
    "producto_id": 15,
    "producto_codigo": "PROD015",
    "producto_nombre": "Martillo",
    "empresa": "ferreteria",
    "cantidad_vendida": 500,
    "unidades": "unidades",
    "valor_total": 25000.00
  },
  {
    "producto_id": 8,
    "producto_codigo": "BLOQ008",
    "producto_nombre": "Bloque 15x20x40",
    "empresa": "bloquera",
    "cantidad_vendida": 3000,
    "unidades": "unidades",
    "valor_total": 45000.00
  },
  {
    "producto_id": 3,
    "producto_codigo": "ARENA001",
    "producto_nombre": "Arena Fina",
    "empresa": "piedrinera",
    "cantidad_vendida": 150.5,
    "unidades": "m³",
    "valor_total": 7500.00
  }
]
```

---

## 3. Estadísticas Predictivas

### Endpoint
```
GET /api/reportes/estadisticas_predictivas/
```

### Descripción
Proporciona estadísticas predictivas basadas en el historial de ventas, incluyendo:
- Promedios de ventas (diario, semanal, mensual)
- Días restantes estimados de stock
- Tendencia de ventas (creciente, decreciente, estable)
- Alertas de reposición

### Parámetros de Filtro (Query Parameters - Opcionales)
- `empresa`: Empresa a filtrar (`ferreteria`, `bloquera`, `piedrinera`, `todas` - default: `todas`)
- `dias_analisis`: Días hacia atrás para analizar (default: 30)

### Ejemplos de Requests

#### Estadísticas de todas las empresas (últimos 30 días)
```http
GET /api/reportes/estadisticas_predictivas/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Estadísticas de piedrinera (últimos 60 días)
```http
GET /api/reportes/estadisticas_predictivas/?empresa=piedrinera&dias_analisis=60
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Respuesta (Ejemplo)
```json
[
  {
    "empresa": "ferreteria",
    "producto_id": 15,
    "producto_codigo": "PROD015",
    "producto_nombre": "Martillo",
    "stock_actual": 50,
    "stock_minimo": 20,
    "promedio_ventas_diarias": 2.5,
    "promedio_ventas_semanales": 17.5,
    "promedio_ventas_mensuales": 75.0,
    "dias_restantes_estimados": 20,
    "necesita_reposicion": false,
    "tendencia": "creciente",
    "unidades": "unidades"
  },
  {
    "empresa": "bloquera",
    "producto_id": 8,
    "producto_codigo": "BLOQ008",
    "producto_nombre": "Bloque 15x20x40",
    "stock_actual": 500,
    "stock_minimo": 200,
    "promedio_ventas_diarias": 15.0,
    "promedio_ventas_semanales": 105.0,
    "promedio_ventas_mensuales": 450.0,
    "dias_restantes_estimados": 33,
    "necesita_reposicion": false,
    "tendencia": "estable",
    "unidades": "unidades"
  },
  {
    "empresa": "piedrinera",
    "producto_id": 3,
    "producto_codigo": "ARENA001",
    "producto_nombre": "Arena Fina",
    "stock_actual": 25.5,
    "stock_minimo": 10.0,
    "promedio_ventas_diarias": 0.5,
    "promedio_ventas_semanales": 3.5,
    "promedio_ventas_mensuales": 15.0,
    "dias_restantes_estimados": 51,
    "necesita_reposicion": false,
    "tendencia": "decreciente",
    "unidades": "m³"
  }
]
```

### Campos de la Respuesta

- `promedio_ventas_diarias`: Promedio de unidades vendidas por día en el período analizado
- `promedio_ventas_semanales`: Promedio de unidades vendidas por semana
- `promedio_ventas_mensuales`: Promedio de unidades vendidas por mes
- `dias_restantes_estimados`: Días estimados antes de agotar el stock actual (basado en promedio diario)
- `necesita_reposicion`: `true` si el stock actual está por debajo o igual al stock mínimo
- `tendencia`: 
  - `creciente`: Las ventas en la segunda mitad del período son >10% mayores que en la primera mitad
  - `decreciente`: Las ventas en la primera mitad del período son >10% mayores que en la segunda mitad
  - `estable`: Las ventas se mantienen relativamente constantes
  - `null`: No hay suficientes datos para determinar la tendencia

---

## Ejemplos con cURL

### Obtener Inventario Unificado
```bash
curl -X GET http://localhost:8000/api/reportes/inventario_unificado/ \
  -H "Authorization: Bearer tu_token_jwt"
```

### Top 10 Productos Más Vendidos
```bash
curl -X GET "http://localhost:8000/api/reportes/top_productos_vendidos/?limit=10" \
  -H "Authorization: Bearer tu_token_jwt"
```

### Top 5 de Ferretería en Enero 2025
```bash
curl -X GET "http://localhost:8000/api/reportes/top_productos_vendidos/?empresa=ferreteria&limit=5&fecha_desde=2025-01-01&fecha_hasta=2025-01-31" \
  -H "Authorization: Bearer tu_token_jwt"
```

### Estadísticas Predictivas (Últimos 60 días)
```bash
curl -X GET "http://localhost:8000/api/reportes/estadisticas_predictivas/?dias_analisis=60" \
  -H "Authorization: Bearer tu_token_jwt"
```

---

## Ejemplos con JavaScript (Fetch)

### Obtener Inventario Unificado
```javascript
const obtenerInventarioUnificado = async () => {
  const response = await fetch('http://localhost:8000/api/reportes/inventario_unificado/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### Top Productos Más Vendidos
```javascript
const obtenerTopProductos = async (empresa = 'todas', limit = 10, fechaDesde = null, fechaHasta = null) => {
  const params = new URLSearchParams({
    empresa: empresa,
    limit: limit
  });
  
  if (fechaDesde) params.append('fecha_desde', fechaDesde);
  if (fechaHasta) params.append('fecha_hasta', fechaHasta);
  
  const response = await fetch(
    `http://localhost:8000/api/reportes/top_productos_vendidos/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return await response.json();
};

// Ejemplo de uso
obtenerTopProductos('ferreteria', 5, '2025-01-01', '2025-01-31');
```

### Estadísticas Predictivas
```javascript
const obtenerEstadisticasPredictivas = async (empresa = 'todas', diasAnalisis = 30) => {
  const params = new URLSearchParams({
    empresa: empresa,
    dias_analisis: diasAnalisis
  });
  
  const response = await fetch(
    `http://localhost:8000/api/reportes/estadisticas_predictivas/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return await response.json();
};

// Ejemplo de uso
obtenerEstadisticasPredictivas('bloquera', 60);
```

---

## Notas Importantes

1. **Ventas**: Los reportes consideran los movimientos de tipo `SALIDA` como ventas.

2. **Unidades**: 
   - Ferretería y Bloquera usan unidades enteras
   - Piedrinera usa metros cúbicos (m³) con decimales

3. **Valor Total**: Se calcula multiplicando la cantidad vendida por el precio de venta del producto.

4. **Estadísticas Predictivas**: 
   - Solo se calculan para productos activos
   - Si un producto no tiene ventas en el período analizado, los promedios serán `null`
   - Los días restantes estimados solo se calculan si hay un promedio diario > 0

5. **Tendencias**: Se determinan comparando las ventas de la primera mitad del período con la segunda mitad. Se requiere una diferencia del 10% para considerar una tendencia creciente o decreciente.

6. **Filtros de Fecha**: 
   - `fecha_desde` y `fecha_hasta` deben estar en formato `YYYY-MM-DD`
   - Si no se especifican, se analizan todos los movimientos disponibles

---

## Resumen de Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/inventario_unificado/` | GET | Reporte consolidado de inventario |
| `/top_productos_vendidos/` | GET | Ranking de productos más vendidos |
| `/estadisticas_predictivas/` | GET | Estadísticas y predicciones de stock |

Todos los endpoints requieren autenticación mediante JWT.

