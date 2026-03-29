"""
Application configuration settings
"""
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database/Storage files
DB_FILE = DATA_DIR / "finanzas.json"
SCHEMA_VERSION = "2.0.0"

# Migration tracking
MIGRATION_LOG_FILE = DATA_DIR / "migrations.log"

# Import settings
SUPPORTED_IMPORT_FORMATS = ["csv", "xlsx", "xls"]
MAX_IMPORT_FILE_SIZE_MB = 50

# Deduplication settings
DEDUPLICATION_WINDOW_DAYS = 7  # Look back N days for duplicates
DEDUPLICATION_TOLERANCE_AMOUNT = 0.01  # Amount tolerance for fuzzy matching

# API settings
API_TITLE = "API de Finanzas Personales"
API_VERSION = "2.0.0"
API_DESCRIPTION = """
API REST completa para gestión de finanzas personales.

Características:
- Gestión de cuentas, tarjetas de crédito y wallets crypto
- Registro y categorización de transacciones
- Importación de datos desde Excel/CSV (MercadoPago, bancos, etc.)
- Tracking de activos, pasivos y patrimonio neto
- Presupuestos y gastos recurrentes
- Analytics y reportes
"""

# CORS settings
CORS_ORIGINS = ["*"]  # In production, restrict to specific origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
