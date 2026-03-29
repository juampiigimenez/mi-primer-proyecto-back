# Arquitectura del Sistema - Finanzas Personales v2.0

## Estructura del Proyecto

```
finanzas-back/
├── app/
│   ├── models/          # Modelos de dominio (Pydantic schemas)
│   │   ├── __init__.py
│   │   ├── enums.py     # Enums compartidos
│   │   ├── account.py   # Account, CreditCard
│   │   ├── transaction.py   # Transaction, ImportBatch, RawImportRow
│   │   ├── category.py  # Category, RecurringExpense, Budget
│   │   ├── asset.py     # Asset, Liability, NetWorthSnapshot
│   │   └── crypto.py    # CryptoWallet, CryptoPosition
│   │
│   ├── services/        # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── importer.py  # Importación CSV/Excel (MercadoPago, etc.)
│   │   ├── classifier.py # Auto-clasificación de transacciones
│   │   └── analytics.py # Generación de reportes y gráficos
│   │
│   ├── repositories/    # Acceso a datos
│   │   ├── __init__.py
│   │   └── json_repository.py # Storage JSON con migraciones
│   │
│   ├── routers/         # API endpoints
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── accounts.py
│   │   ├── imports.py
│   │   └── analytics.py
│   │
│   ├── schemas/         # Response schemas
│   │   └── __init__.py
│   │
│   └── main.py          # FastAPI app principal
│
├── config/
│   ├── __init__.py
│   └── settings.py      # Configuración centralizada
│
├── migrations/
│   ├── __init__.py
│   └── seed_data.py     # Seed data inicial (categorías, etc.)
│
├── data/                # Archivos de datos (gitignored)
│   └── finanzas.json    # Base de datos JSON
│
├── tests/               # Tests unitarios
│
├── main.py              # Entrypoint legacy (v1.0.0) - DEPRECATED
├── storage.py           # Storage legacy - DEPRECATED
├── requirements.txt
├── README.md
└── ARCHITECTURE.md      # Este archivo
```

## Modelo de Datos v2.0

### Entidades Principales

#### 1. **Accounts** (`accounts`)
Cuentas bancarias y de efectivo.
- Campos: name, account_type, currency, balance, bank_name, account_number
- Tipos: checking, savings, cash, investment, crypto, other

#### 2. **Credit Cards** (`credit_cards`)
Tarjetas de crédito.
- Campos: name, bank_name, last_four_digits, credit_limit, current_balance, closing_day, due_day
- Calcula: available_credit

#### 3. **Transactions** (`transactions`)
Transacciones financieras con metadata completa.
- **Tipos**: income, expense, transfer, refund, adjustment
- **Nature**: fixed, variable, debt_payment, investment, savings, income_salary, etc.
- **Status**: pending, confirmed, duplicated, ignored
- **Source**: manual, mercadopago_excel/csv, telegram, bank_statement, crypto_wallet, etc.
- Campos clave:
  - `operation_date` / `posting_date`: fechas de operación e imputación
  - `merchant` / `description`: comercio y descripción
  - `category_id` / `suggested_category_id`: categoría final y sugerida
  - `account_id` / `credit_card_id`: cuenta o tarjeta asociada
  - `deduplication_key`: clave para detectar duplicados
  - `raw_metadata`: metadata original importada
  - `tags`: etiquetas libres

#### 4. **Transaction Import Batches** (`transaction_import_batches`)
Lotes de importación de transacciones.
- Tracking de: total_rows, processed_rows, failed_rows, duplicated_rows
- Status: processing, completed, failed

#### 5. **Raw Import Rows** (`raw_import_rows`)
Filas originales importadas (trazabilidad).
- Almacena: raw_data completo, errores de parsing, transaction_id creada

#### 6. **Categories** (`categories`)
Categorías jerárquicas para transacciones.
- Soporte para subcategorías (parent_id)
- Campos visuales: color, icon
- Seed data con categorías comunes

#### 7. **Recurring Expenses** (`recurring_expenses`)
Gastos recurrentes (subscripciones, servicios fijos).
- Frecuencia: daily, weekly, monthly, yearly
- Vinculación a account/credit_card

#### 8. **Budgets** (`budgets`)
Presupuestos por categoría y período.
- Campos: amount, period (monthly, quarterly, yearly)
- Alert threshold: alerta al alcanzar % del presupuesto

#### 9. **Assets** (`assets`)
Activos (cuentas, inversiones, bienes).
- Tipos: cash, bank_account, investment, crypto, real_estate, vehicle
- Tracking de: value, acquisition_cost, is_liquid

#### 10. **Liabilities** (`liabilities`)
Pasivos (deudas, préstamos).
- Tipos: credit_card, loan, mortgage, debt
- Campos: balance, interest_rate, minimum_payment, due_date

#### 11. **Net Worth Snapshots** (`net_worth_snapshots`)
Snapshots de patrimonio neto en el tiempo.
- Calcula: total_assets - total_liabilities = net_worth
- Para tracking de evolución patrimonial

#### 12. **Crypto Wallets** (`crypto_wallets`)
Wallets de criptomonedas.
- Networks: bitcoin, ethereum, binance_smart_chain, polygon, arbitrum, etc.
- Tipos: hot, cold, exchange, hardware

#### 13. **Crypto Positions** (`crypto_positions`)
Posiciones en criptomonedas.
- Tracking de: quantity, average_buy_price, current_price, total_value
- Calcula: unrealized_pnl, unrealized_pnl_percentage

## Sistema de Storage

### JSONDatabase
- Storage local-first en JSON (`data/finanzas.json`)
- **Schema versioning**: Migración automática de v1.0.0 → v2.0.0
- **Backups automáticos**: Se crean backups antes de migraciones
- **Operaciones**: CRUD completo + query con filter functions
- **Singleton**: Instancia única via `get_db()`

### Migraciones
- Migración automática de `transacciones.json` (v1.0.0) a nuevo schema (v2.0.0)
- Crea cuenta y categoría por defecto para transacciones migradas
- Logs de migración en metadata

## Reglas de Negocio

### Clasificación de Transacciones
- **Automática** via ML/rules (próxima fase)
- **Manual** con sugerencias
- Diferenciación automática income/expense basada en monto y fuente

### Deduplicación
- `deduplication_key`: generada por combinación de fecha + monto + merchant
- Window de búsqueda: 7 días (configurable)
- Tolerancia de monto: 0.01 (configurable)
- Status: duplicated para transacciones detectadas

### Gastos Fijos vs Variables
- Flag `is_fixed_expense` en Transaction
- Nature: fixed, variable, debt_payment, investment, savings

### Soft Reconciliation Rules
- Match por fecha + monto ± tolerancia
- Match por deduplication_key
- Match por merchant similarity

## Extensibilidad

### Preparación para Integraciones Futuras

#### 1. Telegram Bot
- SourceType: telegram_text, telegram_photo
- Parseo de mensajes de texto y OCR de fotos
- Creación de transacciones via bot

#### 2. Resúmenes Bancarios
- SourceType: bank_statement
- Parsers específicos por banco
- Importación vía PDF/Email

#### 3. Tarjetas de Crédito
- SourceType: credit_card_statement
- Tracking de resúmenes mensuales
- Vinculación a CreditCard entity

#### 4. Wallets Crypto / Exchanges
- SourceType: crypto_wallet, exchange_api
- Integración con APIs de exchanges (Binance, Coinbase, etc.)
- Actualización automática de precios
- Tracking de posiciones

## Configuración

Ver `config/settings.py` para configuración centralizada:
- Paths de datos
- Versión de schema
- Límites de importación
- Parámetros de deduplicación
- CORS y API settings

## Próximos Pasos (Siguientes Fases)

- [ ] **Fase 3**: Implementar importador MercadoPago (CSV/Excel)
- [ ] **Fase 4**: Crear routers API REST completos
- [ ] **Fase 5**: Implementar analytics y dashboards (Plotly)
- [ ] **Fase 6**: Sistema de clasificación automática
- [ ] **Fase 7**: Tests unitarios
- [ ] **Fase 8**: Integraciones (Telegram, exchanges)
