# 🧪 Guía de Testing Local - Importador MercadoPago

## 📋 Pre-requisitos

- Python 3.9+ instalado
- pip actualizado

## 🚀 Setup Inicial (Primera Vez)

### 1. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- FastAPI + Uvicorn (API server)
- Pydantic (validación)
- Pandas + openpyxl (procesamiento CSV/Excel)
- Plotly (gráficos - futuro)

### 3. Verificar instalación

```bash
python -c "import fastapi, pandas, openpyxl; print('✅ Dependencias OK')"
```

---

## ▶️ Iniciar el Servidor

```bash
# Opción 1: Uvicorn directo
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Opción 2: Python directo
python -m uvicorn app.main:app --reload

# Opción 3: Script Python
python app/main.py
```

Deberías ver:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🌐 Verificar que el servidor funciona

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### Test 2: Root Endpoint

```bash
curl http://localhost:8000/
```

**Respuesta esperada:**
```json
{
  "name": "API de Finanzas Personales",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "docs": "/docs",
    "redoc": "/redoc",
    "health": "/health"
  }
}
```

### Test 3: Swagger UI

Abrir en navegador:
```
http://localhost:8000/docs
```

Deberías ver la documentación interactiva con todos los endpoints.

---

## 📤 Probar Importación de MercadoPago

### Opción A: Desde Swagger UI (Más Fácil)

1. Abrir http://localhost:8000/docs
2. Expandir `POST /api/v1/imports/upload`
3. Click en "Try it out"
4. Seleccionar archivo: `data/mercadopago_full_ejemplo.csv`
5. Elegir `source_type`: `mercadopago_csv`
6. Click en "Execute"

### Opción B: Con cURL (Línea de Comandos)

```bash
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@data/mercadopago_full_ejemplo.csv" \
  -F "source_type=mercadopago_csv"
```

### Opción C: Con Python requests

```python
import requests

files = {'file': open('data/mercadopago_full_ejemplo.csv', 'rb')}
data = {'source_type': 'mercadopago_csv'}

response = requests.post(
    'http://localhost:8000/api/v1/imports/upload',
    files=files,
    data=data
)

print(response.json())
```

---

## ✅ Respuesta Esperada de Importación

```json
{
  "message": "Importación completada",
  "batch": {
    "id": "batch_abc123def456",
    "source_type": "mercadopago_csv",
    "filename": "mercadopago_full_ejemplo.csv",
    "total_rows": 14,
    "processed_rows": 14,
    "failed_rows": 0,
    "duplicated_rows": 0,
    "status": "completado",
    "created_at": "2026-03-29T...",
    "completed_at": "2026-03-29T...",
    "metadata": {
      "review_required": 0
    }
  }
}
```

---

## 🔍 Verificar Resultados

### Ver todos los batches importados

```bash
curl http://localhost:8000/api/v1/imports/batches
```

### Ver transacciones de un batch específico

```bash
# Reemplazar {batch_id} con el ID real del batch
curl http://localhost:8000/api/v1/imports/batches/{batch_id}/transactions
```

### Ver datos crudos (debugging)

```bash
curl http://localhost:8000/api/v1/imports/batches/{batch_id}/raw
```

---

## 📊 Verificar Base de Datos

El archivo JSON se crea automáticamente:

```bash
# Ver estructura
cat data/finanzas.json | python -m json.tool | head -50

# Ver metadata
cat data/finanzas.json | python -m json.tool | grep -A 5 "_metadata"

# Ver transacciones
cat data/finanzas.json | python -m json.tool | grep -A 20 "transactions"

# Contar transacciones importadas
cat data/finanzas.json | python -m json.tool | grep '"transaction_type"' | wc -l
```

---

## 🧹 Limpiar Datos de Prueba

Para volver a probar desde cero:

```bash
# Detener servidor (Ctrl+C)

# Eliminar base de datos
rm data/finanzas.json

# Eliminar backups
rm data/*.backup

# Reiniciar servidor
uvicorn app.main:app --reload
```

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError

**Problema:** No se encuentran módulos instalados

**Solución:**
```bash
# Verificar que el venv esté activado
which python  # debe mostrar ruta dentro de venv/

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: Port already in use

**Problema:** Puerto 8000 ya ocupado

**Solución:**
```bash
# Opción 1: Usar otro puerto
uvicorn app.main:app --reload --port 8001

# Opción 2: Matar proceso en puerto 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Opción 2: Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: File not found al importar

**Problema:** Ruta del archivo incorrecta

**Solución:**
```bash
# Verificar que el archivo existe
ls -la data/mercadopago_full_ejemplo.csv

# Usar ruta absoluta
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@$(pwd)/data/mercadopago_full_ejemplo.csv" \
  -F "source_type=mercadopago_csv"
```

### Error: Invalid CSV encoding

**Problema:** Encoding del CSV no soportado

**Solución:** El importador intenta múltiples encodings (UTF-8, Latin-1, ISO-8859-1). Si falla, convertir el archivo:
```bash
# Convertir a UTF-8
iconv -f WINDOWS-1252 -t UTF-8 archivo.csv > archivo_utf8.csv
```

---

## ✅ Checklist de Testing Manual

Antes de hacer commit, verificar:

- [ ] Servidor inicia sin errores
- [ ] Health check responde OK
- [ ] Swagger UI se carga correctamente
- [ ] Se puede importar `mercadopago_full_ejemplo.csv`
- [ ] El batch se crea con status "completado"
- [ ] Se procesan las 14 filas
- [ ] No hay failed_rows
- [ ] Las transacciones se crean con campos correctos
- [ ] Se clasifican tipos correctamente (ingreso/gasto/transferencia)
- [ ] Se sugieren categorías
- [ ] Los merchants se normalizan
- [ ] Se genera deduplication_key
- [ ] Se preserva raw_metadata
- [ ] Se puede consultar GET /batches
- [ ] Se puede consultar GET /batches/{id}/transactions
- [ ] Los errores devuelven mensajes claros

---

## 📝 Testing con Archivo Real de MercadoPago

### Preparar tu archivo:

1. Descargar reporte de MercadoPago (CSV o Excel)
2. Colocar en `data/mi_reporte_mp.csv`
3. Importar:

```bash
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@data/mi_reporte_mp.csv" \
  -F "source_type=mercadopago_csv"
```

### Verificar resultados:

```bash
# Ver resumen
curl http://localhost:8000/api/v1/imports/batches | python -m json.tool

# Ver transacciones importadas
batch_id="..."  # Copiar del resultado anterior
curl "http://localhost:8000/api/v1/imports/batches/$batch_id/transactions" | python -m json.tool
```

---

## 🎯 Expected Outputs por Tipo de Transacción

### Compra en supermercado:
```json
{
  "transaction_type": "gasto",
  "merchant_normalized": "carrefour",
  "suggested_category_id": "groceries",
  "category_confidence": 0.90
}
```

### Transferencia recibida:
```json
{
  "transaction_type": "ingreso",
  "suggested_category_id": "transfer",
  "nature": "ingreso_otro"
}
```

### Suscripción (Netflix, Spotify):
```json
{
  "transaction_type": "gasto",
  "suggested_category_id": "subscriptions",
  "nature": "fijo"
}
```

### Pago de servicio (luz, gas):
```json
{
  "transaction_type": "gasto",
  "suggested_category_id": "utilities",
  "nature": "fijo"
}
```

---

## 🔄 Workflow Completo de Testing

```bash
# 1. Setup (solo primera vez)
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt

# 2. Iniciar servidor
uvicorn app.main:app --reload

# 3. En otra terminal - Test health
curl http://localhost:8000/health

# 4. Importar archivo de ejemplo
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@data/mercadopago_full_ejemplo.csv" \
  -F "source_type=mercadopago_csv"

# 5. Ver resultados
curl http://localhost:8000/api/v1/imports/batches | python -m json.tool

# 6. Verificar base de datos
cat data/finanzas.json | python -m json.tool | head -100

# 7. Limpiar para nueva prueba
rm data/finanzas.json
```

---

## 📞 Próximos Pasos

Después de validar que funciona localmente:

1. ✅ Testing manual completo
2. ✅ Verificar todos los campos
3. ✅ Probar con archivo real de MercadoPago
4. ✅ Documentar cualquier issue encontrado
5. ✅ Commit a Git
6. 🔜 Integrar con frontend
7. 🔜 Desplegar a producción
