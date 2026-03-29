# Importador de Transacciones - Guía de Uso

## 🎯 FASE 3 COMPLETADA

El sistema ahora soporta importación de archivos CSV/Excel de MercadoPago con todas las funcionalidades requeridas.

---

## 📋 Endpoints Disponibles

### 1. **POST** `/api/v1/imports/upload`

Subir y procesar archivo CSV/Excel de MercadoPago.

**Parámetros (form-data):**
- `file`: Archivo CSV o Excel (required)
- `source_type`: Tipo de fuente (required)
  - `mercadopago_csv`
  - `mercadopago_excel`
- `account_id`: ID de cuenta por defecto (optional)
- `credit_card_id`: ID de tarjeta por defecto (optional)

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@mercadopago_ejemplo.csv" \
  -F "source_type=mercadopago_csv"
```

**Ejemplo con Python:**
```python
import requests

files = {'file': open('mercadopago_ejemplo.csv', 'rb')}
data = {'source_type': 'mercadopago_csv'}

response = requests.post(
    'http://localhost:8000/api/v1/imports/upload',
    files=files,
    data=data
)
print(response.json())
```

**Respuesta:**
```json
{
  "message": "Importación completada",
  "batch": {
    "id": "batch_abc123def456",
    "source_type": "mercadopago_csv",
    "filename": "mercadopago_ejemplo.csv",
    "total_rows": 14,
    "processed_rows": 14,
    "failed_rows": 0,
    "duplicated_rows": 0,
    "status": "completado",
    "created_at": "2026-03-29T...",
    "completed_at": "2026-03-29T..."
  }
}
```

---

### 2. **GET** `/api/v1/imports/batches`

Obtener todos los lotes de importación.

```bash
curl http://localhost:8000/api/v1/imports/batches
```

---

### 3. **GET** `/api/v1/imports/batches/{batch_id}`

Obtener detalles de un lote específico.

```bash
curl http://localhost:8000/api/v1/imports/batches/batch_abc123def456
```

---

### 4. **GET** `/api/v1/imports/batches/{batch_id}/transactions`

Obtener todas las transacciones de un lote.

```bash
curl http://localhost:8000/api/v1/imports/batches/batch_abc123def456/transactions
```

---

### 5. **GET** `/api/v1/imports/batches/{batch_id}/raw`

Obtener datos crudos importados (para debugging).

```bash
curl http://localhost:8000/api/v1/imports/batches/batch_abc123def456/raw
```

---

## 🔧 Funcionalidades Implementadas

### ✅ Auto-detección Ingreso/Gasto
El sistema detecta automáticamente si es ingreso o gasto basándose en el signo del monto:
- **Monto positivo** → `transaction_type: "ingreso"`
- **Monto negativo** → `transaction_type: "gasto"` (monto se convierte a positivo)

### ✅ Sistema de Deduplicación
- Genera `deduplication_key` usando: fecha + monto + primeros 30 caracteres de descripción
- Busca duplicados en ventana de ±7 días (configurable en `config/settings.py`)
- Tolerancia de monto: ±0.01 (configurable)
- Transacciones duplicadas se marcan con `status: "duplicada"`

### ✅ Extracción de Merchant
Extrae automáticamente el nombre del comercio de la descripción usando separadores comunes:
- `"Supermercado Carrefour - Compra"` → Merchant: `"Supermercado Carrefour"`
- `"Netflix - Suscripción"` → Merchant: `"Netflix"`

### ✅ Trazabilidad Completa
Cada transacción guarda:
- `import_batch_id`: ID del lote de importación
- `raw_import_row_id`: ID de la fila original importada
- `raw_metadata`: Datos completos de la fila original (JSON)
- `tags`: `["importado", "mercadopago"]`

### ✅ Gestión de Errores
- Cada fila se procesa individualmente
- Errores no detienen el proceso completo
- Filas fallidas se registran con mensaje de error
- Batch final reporta: processed_rows, failed_rows, duplicated_rows

---

## 📊 Formato de Archivo MercadoPago

### Columnas Requeridas
El importador espera **al menos** estas columnas (names flexibles):

- **Fecha** / Date / Fecha de Creación
- **Descripción** / Description / Concepto
- **Monto** / Amount / Importe

### Columnas Opcionales
- **Estado** / Status
- **ID** / ID de Operación
- **Tipo** / Type

### Ejemplo CSV
```csv
Fecha,Descripción,Monto,Estado,ID
2026-03-01,Supermercado Carrefour - Compra,-5432.50,Aprobado,1234567890
2026-03-02,Transferencia recibida - Juan Pérez,15000.00,Acreditado,1234567891
2026-03-03,Netflix - Suscripción mensual,-2199.00,Aprobado,1234567892
```

### Normalización Automática
El importador normaliza automáticamente:
- ✅ Nombres de columnas (ignora tildes, mayúsculas/minúsculas)
- ✅ Fechas (parseo flexible)
- ✅ Montos (conversión a float)
- ✅ Encodings (UTF-8, Latin-1, ISO-8859-1)

---

## 🧪 Testing

### 1. Iniciar el servidor
```bash
uvicorn app.main:app --reload
```

### 2. Ejecutar seed data (opcional)
```bash
python migrations/seed_data.py
```

### 3. Importar archivo de ejemplo
```bash
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@data/mercadopago_ejemplo.csv" \
  -F "source_type=mercadopago_csv"
```

### 4. Ver resultados en Swagger UI
Abrir: http://localhost:8000/docs

---

## ⚙️ Configuración

Editar `config/settings.py`:

```python
# Deduplication settings
DEDUPLICATION_WINDOW_DAYS = 7  # Buscar duplicados en ±7 días
DEDUPLICATION_TOLERANCE_AMOUNT = 0.01  # Tolerancia de monto

# Import settings
MAX_IMPORT_FILE_SIZE_MB = 50  # Tamaño máximo de archivo
SUPPORTED_IMPORT_FORMATS = ["csv", "xlsx", "xls"]
```

---

## 🔍 Debugging

### Ver datos crudos importados
```bash
# Listar todos los batches
curl http://localhost:8000/api/v1/imports/batches

# Ver raw data de un batch específico
curl http://localhost:8000/api/v1/imports/batches/batch_abc123/raw
```

### Verificar en base de datos JSON
```bash
cat data/finanzas.json | jq '.transaction_import_batches'
cat data/finanzas.json | jq '.raw_import_rows'
cat data/finanzas.json | jq '.transactions'
```

---

## 🚀 Próximos Pasos

### Mejoras futuras sugeridas:
- [ ] Clasificación automática de categorías (ML)
- [ ] Soporte para más formatos (banco, tarjetas)
- [ ] Bulk edit de transacciones importadas
- [ ] Preview antes de confirmar importación
- [ ] Reglas custom de parseo por usuario
- [ ] Importación programada (cron)
- [ ] Integración con APIs de MercadoPago
