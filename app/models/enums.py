"""
Enums and constants for the finance application
"""
from enum import Enum


class TransactionType(str, Enum):
    """Type of transaction"""
    INCOME = "ingreso"
    EXPENSE = "gasto"
    TRANSFER = "transferencia"
    REFUND = "reembolso"
    ADJUSTMENT = "ajuste"


class TransactionNature(str, Enum):
    """Nature/category of transaction"""
    FIXED = "fijo"  # Gastos fijos (alquiler, servicios)
    VARIABLE = "variable"  # Gastos variables (comida, entretenimiento)
    DEBT_PAYMENT = "pago_deuda"  # Pago de deudas
    INVESTMENT = "inversion"  # Inversiones
    SAVINGS = "ahorro"  # Ahorros
    INCOME_SALARY = "ingreso_salario"  # Ingreso por salario
    INCOME_FREELANCE = "ingreso_freelance"  # Ingreso freelance
    INCOME_OTHER = "ingreso_otro"  # Otros ingresos


class TransactionStatus(str, Enum):
    """Status of transaction"""
    PENDING = "pendiente"
    CONFIRMED = "confirmada"
    DUPLICATED = "duplicada"
    IGNORED = "ignorada"


class SourceType(str, Enum):
    """Source of transaction data"""
    MANUAL = "manual"
    MERCADOPAGO_EXCEL = "mercadopago_excel"
    MERCADOPAGO_CSV = "mercadopago_csv"
    TELEGRAM_TEXT = "telegram_texto"
    TELEGRAM_PHOTO = "telegram_foto"
    BANK_STATEMENT = "resumen_bancario"
    CREDIT_CARD_STATEMENT = "resumen_tarjeta"
    CRYPTO_WALLET = "wallet_crypto"
    EXCHANGE_API = "exchange_api"


class AccountType(str, Enum):
    """Type of financial account"""
    CHECKING = "cuenta_corriente"  # Cuenta corriente
    SAVINGS = "caja_ahorro"  # Caja de ahorro
    CASH = "efectivo"  # Efectivo
    INVESTMENT = "inversion"  # Cuenta de inversión
    CRYPTO = "crypto"  # Wallet crypto
    OTHER = "otro"


class CryptoNetwork(str, Enum):
    """Blockchain networks"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"
    CARDANO = "cardano"
    OTHER = "otro"


class Currency(str, Enum):
    """Supported currencies"""
    ARS = "ARS"  # Peso argentino
    USD = "USD"  # Dólar estadounidense
    EUR = "EUR"  # Euro
    BRL = "BRL"  # Real brasileño
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum
    USDT = "USDT"  # Tether
    USDC = "USDC"  # USD Coin
    DAI = "DAI"  # Dai stablecoin


class AssetType(str, Enum):
    """Type of asset"""
    CASH = "efectivo"
    BANK_ACCOUNT = "cuenta_bancaria"
    INVESTMENT = "inversion"
    CRYPTO = "crypto"
    REAL_ESTATE = "inmueble"
    VEHICLE = "vehiculo"
    OTHER = "otro"


class LiabilityType(str, Enum):
    """Type of liability"""
    CREDIT_CARD = "tarjeta_credito"
    LOAN = "prestamo"
    MORTGAGE = "hipoteca"
    DEBT = "deuda"
    OTHER = "otro"
