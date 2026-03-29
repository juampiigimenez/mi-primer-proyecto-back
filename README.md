# API de Finanzas Personales v2.0

API REST completa para gestión de finanzas personales con importador robusto de MercadoPago.

## ✨ Características Principales

- ✅ **Importador MercadoPago** - Soporta CSV/Excel con todas las columnas oficiales
- ✅ **Clasificación Automática** - Detecta ingresos, gastos, transferencias, reembolsos
- ✅ **Categorización Inteligente** - 20+ categorías con confianza medible
- ✅ **Normalización de Merchants** - Limpieza y estandarización automática
- ✅ **Deduplicación Avanzada** - Previene importaciones duplicadas
- ✅ **Trazabilidad Completa** - Preserva datos originales para auditoría
- ✅ **API REST** - Documentación Swagger interactiva
- ✅ **Local-First** - Almacenamiento JSON sin dependencias externas

---

## 🚀 Quick Start

### Opción 1: Scripts Automáticos (Recomendado)

**Windows:**
```bash
setup.bat    # Instalar dependencias
start.bat    # Iniciar servidor
```

**Linux/Mac:**
```bash
./setup.sh   # Instalar dependencias
./start.sh   # Iniciar servidor
```

### Opción 2: Manual

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar servidor
uvicorn app.main:app --reload
```

Abrir navegador en: **http://localhost:8000/docs**

---

## 📦 Stack Tecnológico

- **FastAPI** 0.104.1 - Framework web moderno
- **Pydantic** 2.5.0 - Validación de datos
- **Pandas** 2.1.3 - Procesamiento de datos
- **openpyxl** 3.1.2 - Soporte Excel
- **Uvicorn** 0.24.0 - Servidor ASGI

---

## 📋 Endpoints Principales

### Importación

- `POST /api/v1/imports/upload` - Subir archivo CSV/Excel
- `GET /api/v1/imports/batches` - Listar todos los lotes
- `GET /api/v1/imports/batches/{id}` - Detalles de un lote
- `GET /api/v1/imports/batches/{id}/transactions` - Transacciones de un lote
- `GET /api/v1/imports/batches/{id}/raw` - Datos crudos (debugging)

### Sistema

- `GET /` - Información de la API
- `GET /health` - Health check
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

---

## 📤 Ejemplo de Uso: Importar Archivo MercadoPago

### Desde Swagger UI (Más Fácil)

1. Abrir http://localhost:8000/docs
2. Expandir `POST /api/v1/imports/upload`
3. Click "Try it out"
4. Seleccionar archivo: `data/mercadopago_full_ejemplo.csv`
5. Elegir `source_type`: `mercadopago_csv`
6. Click "Execute"

### Desde cURL

```bash
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@data/mercadopago_full_ejemplo.csv" \
  -F "source_type=mercadopago_csv"
```

### Respuesta Esperada

```json
{
  "message": "Importación completada",
  "batch": {
    "id": "batch_abc123",
    "filename": "mercadopago_full_ejemplo.csv",
    "total_rows": 14,
    "processed_rows": 14,
    "failed_rows": 0,
    "duplicated_rows": 0,
    "status": "completado",
    "metadata": {
      "review_required": 0
    }
  }
}
```

---

## 🎯 Columnas de MercadoPago Soportadas

El importador procesa automáticamente **48 columnas oficiales** de MercadoPago:

**Prioritarias (mapeadas al modelo):**
- `SOURCE_ID`, `EXTERNAL_REFERENCE`, `ORDER_ID`
- `TRANSACTION_DATE`, `SETTLEMENT_DATE`, `MONEY_RELEASE_DATE`
- `TRANSACTION_AMOUNT`, `REAL_AMOUNT`, `SETTLEMENT_NET_AMOUNT`
- `TRANSACTION_TYPE`, `DESCRIPTION`, `PAYMENT_METHOD`
- `STORE_NAME`, `POS_NAME`, `PAYER_NAME`
- `INSTALLMENTS`, `CARD_INITIAL_NUMBER`
- Y 30+ más...

**Secundarias (guardadas en raw_metadata para trazabilidad):**
- `USER_ID`, `PACK_ID`, `SHIPPING_ID`, `TAXES_AMOUNT`, etc.

Ver documentación completa en: [IMPORTADOR_MERCADOPAGO_ROBUSTO.md](IMPORTADOR_MERCADOPAGO_ROBUSTO.md)

---

## 🤖 Clasificación y Categorización Automática

### Tipos de Transacción Detectados

| Tipo | Ejemplos |
|------|----------|
| `ingreso` | Salario, freelance, cobros, ventas |
| `gasto` | Compras, pagos, servicios, suscripciones |
| `transferencia` | Movimientos entre cuentas propias |
| `reembolso` | Devoluciones, contracargos |
| `ajuste` | Ajustes técnicos/contables |

### Categorías Automáticas (20+)

```
groceries, food_delivery, restaurants, transport, fuel,
shopping, health, pharmacy, entertainment, subscriptions,
services, utilities, rent, education, salary, investment,
savings, credit_card_payment, taxes, transfer, refund
```

### Normalización de Merchants

```
"CARREFOUR EXPRESS 1234" → "carrefour"
"UBER *TRIP ABC" → "uber"
"MERCADO LIBRE SRL" → "mercadolibre"
```

---

## 📂 Estructura del Proyecto

```
finanzas-back/
├── app/
│   ├── main.py                    # Aplicación FastAPI principal
│   ├── models/                    # Modelos Pydantic
│   │   ├── enums.py              # Enums en español
│   │   ├── transaction.py        # Modelo de transacciones (extendido)
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── asset.py
│   │   └── crypto.py
│   ├── services/                  # Lógica de negocio
│   │   ├── importer.py           # Facade del importador
│   │   ├── importer_robust.py    # Parser MercadoPago completo
│   │   ├── classifier.py         # Clasificación multi-señal
│   │   ├── categorizer.py        # Categorización automática
│   │   └── merchant_normalizer.py # Normalización de merchants
│   ├── repositories/              # Acceso a datos
│   │   └── json_repository.py    # Storage JSON con migraciones
│   └── routers/                   # API endpoints
│       └── imports.py
├── config/
│   └── settings.py               # Configuración centralizada
├── migrations/
│   └── seed_data.py              # Datos iniciales (categorías)
├── data/
│   ├── .gitkeep
│   ├── mercadopago_ejemplo.csv        # Ejemplo básico (14 filas)
│   └── mercadopago_full_ejemplo.csv   # Ejemplo completo (todas las columnas)
├── tests/
│   └── test_enums_spanish.py
├── setup.bat / setup.sh          # Scripts de instalación
├── start.bat / start.sh          # Scripts de inicio rápido
├── requirements.txt              # Dependencias Python
├── TESTING_LOCAL.md              # Guía completa de testing
├── IMPORTADOR_MERCADOPAGO_ROBUSTO.md  # Documentación técnica
└── README.md                     # Este archivo
```

---

## 🧪 Testing Local

Ver guía completa en: [TESTING_LOCAL.md](TESTING_LOCAL.md)

**Checklist rápido:**
```bash
# 1. Setup
./setup.sh  # o setup.bat en Windows

# 2. Iniciar
./start.sh  # o start.bat en Windows

# 3. Test health
curl http://localhost:8000/health

# 4. Importar ejemplo
curl -X POST "http://localhost:8000/api/v1/imports/upload" \
  -F "file=@data/mercadopago_full_ejemplo.csv" \
  -F "source_type=mercadopago_csv"

# 5. Ver resultados
curl http://localhost:8000/api/v1/imports/batches
```

---

## 📊 Base de Datos

**Archivo:** `data/finanzas.json`

**Schema v2.0.0** con colecciones:
- `transactions` - Transacciones procesadas
- `transaction_import_batches` - Lotes de importación
- `raw_import_rows` - Datos crudos (trazabilidad)
- `accounts` - Cuentas bancarias
- `credit_cards` - Tarjetas de crédito
- `categories` - Categorías
- `assets`, `liabilities`, `net_worth_snapshots` - Patrimonio
- `crypto_wallets`, `crypto_positions` - Crypto

**Migración automática** desde v1.0.0 (`transacciones.json`) a v2.0.0

---

## ⚙️ Configuración

Editar `config/settings.py`:

```python
# Deduplicación
DEDUPLICATION_WINDOW_DAYS = 7         # Ventana de búsqueda ±7 días
DEDUPLICATION_TOLERANCE_AMOUNT = 0.01  # Tolerancia de monto

# Importación
MAX_IMPORT_FILE_SIZE_MB = 50
SUPPORTED_IMPORT_FORMATS = ["csv", "xlsx", "xls"]

# API
API_TITLE = "API de Finanzas Personales"
API_VERSION = "2.0.0"
CORS_ORIGINS = ["*"]  # Cambiar en producción
```

---

## 🔐 Seguridad

- ✅ CORS configurado (actualizar para producción)
- ✅ Validación de tipos de archivo
- ✅ Archivos temporales limpiados automáticamente
- ✅ No se exponen rutas del sistema
- ⚠️ Sin autenticación (añadir en producción)
- ⚠️ Sin rate limiting (añadir en producción)

---

## 🐛 Troubleshooting

### Puerto ocupado
```bash
# Cambiar puerto
uvicorn app.main:app --reload --port 8001
```

### Módulos no encontrados
```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de encoding en CSV
El importador intenta automáticamente UTF-8, Latin-1 e ISO-8859-1. Si falla, convertir:
```bash
iconv -f WINDOWS-1252 -t UTF-8 archivo.csv > archivo_utf8.csv
```

---

## 📚 Documentación Adicional

- [TESTING_LOCAL.md](TESTING_LOCAL.md) - Guía completa de testing
- [IMPORTADOR_MERCADOPAGO_ROBUSTO.md](IMPORTADOR_MERCADOPAGO_ROBUSTO.md) - Documentación técnica del importador
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del sistema
- [VALORES_ENUMS_ESPAÑOL.md](VALORES_ENUMS_ESPAÑOL.md) - Enums en español

---

## 🚀 Próximas Features

- [ ] Routers CRUD completos (Transactions, Accounts, Categories)
- [ ] Analytics y dashboards con Plotly
- [ ] Machine Learning para categorización
- [ ] Integración con API de MercadoPago (OAuth)
- [ ] Telegram bot para registro de gastos
- [ ] Integración con exchanges crypto
- [ ] Frontend web/mobile
- [ ] Tests unitarios completos
- [ ] CI/CD pipeline

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📄 Licencia

Este proyecto es de uso personal. Todos los derechos reservados.

---

## 👨‍💻 Autor

Desarrollado con ❤️ para gestión de finanzas personales

---

## 📞 Soporte

Para issues o preguntas:
- Ver documentación en `/docs`
- Revisar [TESTING_LOCAL.md](TESTING_LOCAL.md)
- Consultar [IMPORTADOR_MERCADOPAGO_ROBUSTO.md](IMPORTADOR_MERCADOPAGO_ROBUSTO.md)

---

**¡Listo para usar! 🎉**

```bash
./setup.sh && ./start.sh
```

Abrir http://localhost:8000/docs y comenzar a importar transacciones.
