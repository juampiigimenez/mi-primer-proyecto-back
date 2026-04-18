"""
Pytest fixtures for testing
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from app.repositories.json_repository import JSONDatabase


# TODO: Add database isolation - currently tests using client() will hit production database
# Consider using FastAPI dependency overrides or test database configuration
@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def temp_db():
    """Temporary database for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    temp_db_file = temp_dir / "test_finanzas.json"

    db = JSONDatabase(db_file=temp_db_file)

    yield db

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_transaction():
    """Sample transaction data"""
    return {
        "monto": 1500.50,
        "tipo": "ingreso",
        "descripcion": "Salario mensual"
    }


@pytest.fixture
def sample_csv_content():
    """Sample MercadoPago CSV content"""
    return """TRANSACTION_ID,SOURCE_ID,USER_ID,PAYMENT_TYPE,TRANSACTION_TYPE,STATUS,TRANSACTION_AMOUNT,GROSS_AMOUNT,NET_AMOUNT,FEE_AMOUNT,SETTLEMENT_NET_AMOUNT,INSTALLMENTS,INSTALLMENT_AMOUNT,INTEREST_AMOUNT,COUPON_AMOUNT,SHIPPING_COST,TRANSACTION_DETAILS,DESCRIPTION,MERCHANT,PAYMENT_METHOD,PAYMENT_METHOD_TYPE,TRANSACTION_APPROVAL_DATE,TRANSACTION_DATE_CREATED,RECONCILIATION_DATE,COUPON_ID,POS_ID,EXTERNAL_REFERENCE,MP_FEE_AMOUNT,FINANCING_FEE_AMOUNT,SHIPPING_FEE_AMOUNT,TAXES_AMOUNT,INSTALLMENT_PLAN_ID,DEFERRED_PERIOD,WALLET_PARTNER_FEE,COLLECTOR_ID,PAYER_ID,CARD_ID,AUTHORIZATION_CODE,TERMINAL_NUMBER,BATCH_CLOSING_DATE,BATCH_NUMBER,ITEM_ID,ITEM_TITLE,MARKETPLACE,MP_FEE_DETAILS,REAL_AMOUNT,CURRENCY_ID,POSTING_DATE,SETTLEMENT_DATE
123456,789012,34567890,payment,payment,approved,1500.50,1500.50,1450.30,50.20,1450.30,1,1500.50,0,0,0,Payment received,Salario,Empresa SA,account_money,account_money,2024-01-15T10:30:00.000Z,2024-01-15T10:30:00.000Z,2024-01-16,,,REF123,50.20,0,0,0,,,0,12345678,98765432,,,,,,,Product1,Product Title,marketplace,fee_details,1500.50,ARS,2024-01-16,2024-01-17
234567,890123,34567890,payment,payment,approved,250.00,250.00,235.00,15.00,235.00,1,250.00,0,0,0,Payment,Compra supermercado,Carrefour Express,credit_card,credit_card,2024-01-16T15:20:00.000Z,2024-01-16T15:20:00.000Z,2024-01-17,,,REF124,15.00,0,0,0,,,0,12345678,98765432,1234,,,,,,Product2,Groceries,marketplace,fee_details,-250.00,ARS,2024-01-17,2024-01-18"""
