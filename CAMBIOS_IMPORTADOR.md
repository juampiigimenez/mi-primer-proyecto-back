# Cambios en el Importador de Mercado Pago

## Resumen de Correcciones

Este documento describe las correcciones implementadas en el importador y en la aplicación según los requerimientos del usuario.

---

## 1. Corrección de Duplicación de Transacciones

### Problema Anterior
El sistema guardaba SOURCE_IDs procesados en la base de datos, causando que transacciones del mismo archivo no se cargaran si se importaba el mismo archivo múltiples veces.

### Solución Implementada
- Se eliminó la persistencia de SOURCE_IDs en la base de datos
- Se implementó un `Set` en memoria (`current_file_source_ids`) que solo vive durante la importación del archivo
- Cada archivo se procesa completamente sin duplicar transacciones dentro del mismo archivo
- Al importar un nuevo archivo, el set se limpia y todas las transacciones se procesan nuevamente

**Ubicación**: `app/services/importer_simple.py:51-82`

---

## 2. Clasificación Basada en REAL_AMOUNT

### Implementación
- **Si REAL_AMOUNT > 0** → La transacción se clasifica como **Ingreso**
- **Si REAL_AMOUNT < 0** → La transacción se clasifica como **Egreso/Gasto**
- **Si REAL_AMOUNT = 0** → La transacción se ignora

**Ubicación**: `app/services/importer_simple.py:244-252`

---

## 3. Excepción para Tarjeta de Crédito

### Problema
Las transferencias realizadas con tarjeta de crédito aparecían como ingresos falsos cuando REAL_AMOUNT era positivo.

### Solución Implementada
Si `PAYMENT_METHOD_TYPE = 'credit_card'` y `REAL_AMOUNT > 0`, la transacción se **ignora completamente**.

Esto evita que las acreditaciones de tarjeta de crédito (que no son ingresos reales) aparezcan en el sistema.

**Ubicación**: `app/services/importer_simple.py:239-242`

```python
# EXCEPCIÓN: Si PAYMENT_METHOD_TYPE = credit_card y REAL_AMOUNT > 0, ignorar
if payment_method_type == 'credit_card' and real_amount > 0:
    return None
```

---

## 4. Mantener Todas las Columnas Originales

### Implementación
Todas las columnas del archivo CSV se mantienen en el campo `all_columns` de cada transacción.

Esto permite:
- Auditoría completa de los datos originales
- Debugging y análisis posterior
- Acceso a información no mapeada explícitamente

**Ubicación**: `app/services/importer_simple.py:287-291`

```python
# Mantener TODAS las columnas originales del CSV
all_original_columns = {}
for col_name, col_value in row.items():
    if col_value is not None and col_value != '':
        all_original_columns[col_name] = col_value
```

---

## 5. Visualización de Ingresos y Egresos

### Correcciones
- Los ingresos aparecen con su valor **positivo** en la respuesta
- Los egresos aparecen con su valor **positivo** (usando `abs_amount`)
- El tipo se indica con el campo `transaction_type`: `"ingreso"` o `"gasto"`
- El campo `real_amount` conserva el valor original con signo
- **NO se asigna estado "Pendiente"** - todas las transacciones importadas tienen estado `"confirmada"`

**Ubicación**: `app/services/importer_simple.py:274-310`

---

## 6. Moneda en Pesos (ARS)

### Implementación
Toda la aplicación ahora trabaja en **Pesos Argentinos (ARS)**.

- El campo `currency` siempre se fuerza a `"ARS"`
- Independientemente de lo que diga el CSV
- Todos los cálculos y visualizaciones están en ARS

**Ubicación**: `app/services/importer_simple.py:277-279`

```python
# Moneda - SIEMPRE en ARS (Pesos)
currency_str = 'ARS'  # Forzar ARS
```

---

## 7. Botón CONFIRMAR - Endpoint Implementado

### Nuevo Endpoint
```
POST /api/v1/imports/batches/{batch_id}/confirm
```

### Funcionalidad
1. Toma todas las transacciones de un batch importado
2. Las transacciones clasificadas como **ingresos** se registran como ingresos en el dashboard
3. Las transacciones clasificadas como **gastos** se registran como gastos en el dashboard
4. Retorna un resumen con:
   - Cantidad de ingresos confirmados
   - Cantidad de gastos confirmados
   - Total de ingresos en ARS
   - Total de gastos en ARS
   - Total de transacciones procesadas

### Ejemplo de Respuesta
```json
{
  "success": true,
  "batch_id": "abc123...",
  "summary": {
    "ingresos_confirmados": 15,
    "gastos_confirmados": 42,
    "total_ingresos_ars": 125000.50,
    "total_gastos_ars": 87500.75,
    "total_transacciones": 57
  }
}
```

**Ubicación**: `app/routers/imports.py:111-193`

---

## Flujo Completo de Uso

### 1. Importar Archivo
```bash
POST /api/v1/imports/upload
Content-Type: multipart/form-data

file: [archivo.csv]
source_type: mercadopago_csv
```

Respuesta:
```json
{
  "success": true,
  "batch": {
    "id": "batch_abc123",
    "total_rows": 100,
    "processed_rows": 95,
    "duplicated_rows": 3,
    "failed_rows": 2
  }
}
```

### 2. Ver Transacciones del Batch
```bash
GET /api/v1/imports/batches/batch_abc123/transactions
```

Respuesta incluye todas las transacciones con:
- Tipo (ingreso/gasto) basado en REAL_AMOUNT
- Montos siempre positivos
- Moneda en ARS
- Todas las columnas originales en `all_columns`

### 3. Confirmar y Pasar al Dashboard
```bash
POST /api/v1/imports/batches/batch_abc123/confirm
```

Las transacciones ahora aparecen en:
- `GET /transacciones` - Lista de transacciones
- `GET /balance` - Balance total (ingresos - gastos) en ARS

---

## Archivos Modificados

1. **app/services/importer_simple.py**
   - Eliminada deduplicación persistente
   - Implementada clasificación por REAL_AMOUNT
   - Agregada excepción para credit_card
   - Forzado de moneda a ARS
   - Inclusión de todas las columnas originales

2. **app/routers/imports.py**
   - Agregado endpoint `/batches/{batch_id}/confirm`
   - Import de `datetime`
   - Import de `storage`

3. **app/main.py**
   - Actualizada documentación de endpoints

---

## Notas Técnicas

### Deduplicación
La deduplicación ahora solo previene duplicados **dentro del mismo archivo CSV**. Si importas el mismo archivo dos veces, todas las transacciones se procesarán ambas veces. Esto es intencional según los requerimientos.

### Persistencia
Las transacciones confirmadas se guardan en `transacciones.json` (sistema legacy) para mantener compatibilidad con el dashboard existente.

### Formato de Moneda
Todos los montos se manejan como números flotantes. El frontend debe agregar el símbolo "$" o "ARS" según corresponda.

---

## Testing

Para probar las correcciones:

1. Cargar un archivo CSV de Mercado Pago
2. Verificar que no hay duplicados en la respuesta
3. Verificar que los ingresos y gastos están correctamente clasificados
4. Verificar que las transacciones con credit_card y monto positivo NO aparecen
5. Confirmar el batch
6. Verificar que las transacciones aparecen en `/transacciones` y `/balance`
7. Verificar que el balance está en ARS

---

## Fecha de Implementación
2026-04-07
