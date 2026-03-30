# Guía de Testing - Endpoint de Importación Mercado Pago

## Endpoint Implementado

**POST** `/api/v1/imports/upload`

### Descripción
Recibe un archivo CSV o XLSX exportado de Mercado Pago y realiza la importación automática de transacciones.

### Parámetros

#### Form Data
- `file` (requerido): Archivo CSV o XLSX de Mercado Pago
- `source_type` (opcional): Tipo de fuente - se detecta automáticamente basado en la extensión
  - Si es `.csv` → `mercadopago_csv`
  - Si es `.xlsx` o `.xls` → `mercadopago_excel`
- `account_id` (opcional): ID de cuenta para asociar las transacciones
- `credit_card_id` (opcional): ID de tarjeta de crédito para asociar las transacciones

### Respuesta Exitosa

```json
{
  "success": true,
  "message": "Importación completada exitosamente",
  "summary": {
    "total_rows": 150,
    "processed": 145,
    "duplicates": 3,
    "errors": 2,
    "review_required": 5
  },
  "batch_id": "batch_abc123def456",
  "batch": {
    "id": "batch_abc123def456",
    "source_type": "mercadopago_csv",
    "filename": "mercadopago_export.csv",
    "status": "completado",
    "created_at": "2026-03-29T12:00:00",
    "completed_at": "2026-03-29T12:00:05"
  }
}
```

### Columnas Esperadas del CSV/XLSX de Mercado Pago

#### Columnas Principales (Procesadas)
- `TRANSACTION_DATE` → Fecha de la operación
- `TRANSACTION_AMOUNT` → Monto (puede ser negativo para gastos)
- `TRANSACTION_TYPE` → Tipo de transacción MP
- `DESCRIPTION` → Descripción de la transacción
- `STORE_NAME` → Nombre del comercio
- `SOURCE_ID` → ID externo de MP
- `EXTERNAL_REFERENCE` → Referencia externa
- `SETTLEMENT_DATE` → Fecha de liquidación
- `MONEY_RELEASE_DATE` → Fecha de disponibilidad
- `PAYMENT_METHOD` → Método de pago
- `PAYMENT_METHOD_TYPE` → Tipo de método de pago
- `INSTALLMENTS` → Cuotas
- `PAYER_NAME` → Nombre del pagador
- `CARD_INITIAL_NUMBER` → Últimos dígitos de tarjeta

#### Columnas Secundarias (Guardadas en metadata)
Todas las demás columnas de Mercado Pago se guardan en `raw_metadata` para trazabilidad.

## Procesamiento Automático

### 1. Clasificación de Transacciones
Cada fila se clasifica automáticamente en:
- **income** (ingreso): Cobros, ventas, transferencias recibidas
- **expense** (gasto): Compras, pagos, servicios
- **transfer** (transferencia): Movimientos entre cuentas
- **refund** (reembolso): Devoluciones

### 2. Categorización Inteligente
- Asigna categorías basadas en el merchant y descripción
- Proporciona un `category_confidence` (0-1)
- Si la confianza es < 0.6, la transacción se marca para revisión

### 3. Detección de Duplicados
- Genera una clave de deduplicación usando SOURCE_ID o EXTERNAL_REFERENCE
- Si no hay ID externo, usa: fecha + monto + descripción
- Busca duplicados en una ventana de ±7 días con tolerancia de monto

### 4. Normalización de Merchants
- Normaliza nombres de comercios (ej: "MERCADOLIBRE*ENVIO" → "MercadoLibre")
- Extrae merchant de STORE_NAME, POS_NAME o DESCRIPTION

## Ejemplo de Uso con cURL

```bash
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@mercadopago_export.csv" \
  -F "account_id=acc_123"
```

## Ejemplo de Uso con Python

```python
import requests

url = "http://localhost:8000/api/v1/imports/upload"
files = {"file": open("mercadopago_export.csv", "rb")}
data = {"account_id": "acc_123"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Estados de Transacciones Importadas

- `confirmada`: Transacción procesada correctamente con alta confianza
- `pendiente`: Necesita revisión manual (baja confianza de clasificación)
- `duplicada`: Detectada como duplicado de una transacción existente
- `ignorada`: Marcada manualmente para ignorar

## Acceso a Datos Importados

### Ver el batch completo
```
GET /api/v1/imports/batches/{batch_id}
```

### Ver transacciones del batch
```
GET /api/v1/imports/batches/{batch_id}/transactions
```

### Ver filas raw para debugging
```
GET /api/v1/imports/batches/{batch_id}/raw
```

## Instalación y Configuración

### Requisitos
- Python 3.11+ (recomendado Python 3.11 o 3.12, evitar 3.14 por incompatibilidades)
- FastAPI, Pandas, OpenPyXL y otras dependencias en `requirements.txt`

### Setup
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python -m uvicorn app.main:app --reload --port 8000
```

### Verificar que el servidor está funcionando
```bash
curl http://localhost:8000/health
```

Debería retornar:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```
