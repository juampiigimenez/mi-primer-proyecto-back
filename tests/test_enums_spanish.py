"""
Test to verify all enum values are in Spanish
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.enums import (
    TransactionType,
    TransactionNature,
    TransactionStatus,
    SourceType,
    AccountType,
    AssetType,
    LiabilityType
)


def test_transaction_type_spanish():
    """Verify TransactionType values are in Spanish"""
    assert TransactionType.INCOME.value == "ingreso"
    assert TransactionType.EXPENSE.value == "gasto"
    assert TransactionType.TRANSFER.value == "transferencia"
    assert TransactionType.REFUND.value == "reembolso"
    assert TransactionType.ADJUSTMENT.value == "ajuste"
    print("✅ TransactionType: All values in Spanish")


def test_transaction_nature_spanish():
    """Verify TransactionNature values are in Spanish"""
    assert TransactionNature.FIXED.value == "fijo"
    assert TransactionNature.VARIABLE.value == "variable"
    assert TransactionNature.DEBT_PAYMENT.value == "pago_deuda"
    assert TransactionNature.INVESTMENT.value == "inversion"
    assert TransactionNature.SAVINGS.value == "ahorro"
    assert TransactionNature.INCOME_SALARY.value == "ingreso_salario"
    print("✅ TransactionNature: All values in Spanish")


def test_transaction_status_spanish():
    """Verify TransactionStatus values are in Spanish"""
    assert TransactionStatus.PENDING.value == "pendiente"
    assert TransactionStatus.CONFIRMED.value == "confirmada"
    assert TransactionStatus.DUPLICATED.value == "duplicada"
    assert TransactionStatus.IGNORED.value == "ignorada"
    print("✅ TransactionStatus: All values in Spanish")


def test_source_type_spanish():
    """Verify SourceType values are in Spanish"""
    assert SourceType.TELEGRAM_TEXT.value == "telegram_texto"
    assert SourceType.TELEGRAM_PHOTO.value == "telegram_foto"
    assert SourceType.BANK_STATEMENT.value == "resumen_bancario"
    assert SourceType.CREDIT_CARD_STATEMENT.value == "resumen_tarjeta"
    assert SourceType.CRYPTO_WALLET.value == "wallet_crypto"
    print("✅ SourceType: All values in Spanish")


def test_account_type_spanish():
    """Verify AccountType values are in Spanish"""
    assert AccountType.CHECKING.value == "cuenta_corriente"
    assert AccountType.SAVINGS.value == "caja_ahorro"
    assert AccountType.CASH.value == "efectivo"
    assert AccountType.INVESTMENT.value == "inversion"
    assert AccountType.OTHER.value == "otro"
    print("✅ AccountType: All values in Spanish")


def test_asset_type_spanish():
    """Verify AssetType values are in Spanish"""
    assert AssetType.CASH.value == "efectivo"
    assert AssetType.BANK_ACCOUNT.value == "cuenta_bancaria"
    assert AssetType.INVESTMENT.value == "inversion"
    assert AssetType.REAL_ESTATE.value == "inmueble"
    assert AssetType.VEHICLE.value == "vehiculo"
    assert AssetType.OTHER.value == "otro"
    print("✅ AssetType: All values in Spanish")


def test_liability_type_spanish():
    """Verify LiabilityType values are in Spanish"""
    assert LiabilityType.CREDIT_CARD.value == "tarjeta_credito"
    assert LiabilityType.LOAN.value == "prestamo"
    assert LiabilityType.MORTGAGE.value == "hipoteca"
    assert LiabilityType.DEBT.value == "deuda"
    assert LiabilityType.OTHER.value == "otro"
    print("✅ LiabilityType: All values in Spanish")


if __name__ == "__main__":
    print("🧪 Testing enum values are in Spanish...\n")

    test_transaction_type_spanish()
    test_transaction_nature_spanish()
    test_transaction_status_spanish()
    test_source_type_spanish()
    test_account_type_spanish()
    test_asset_type_spanish()
    test_liability_type_spanish()

    print("\n✅ All enum values are correctly in Spanish!")
