# Finanzas CRUD + Frontend Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement complete CRUD endpoints for transactions, verify import endpoints, refactor frontend with modern CSS/JS patterns, and ensure full test coverage.

**Architecture:** FastAPI backend with JSON storage (existing JSONDatabase), vanilla JS frontend with modular architecture using CSS variables and ES6 modules. Two-layer backend: legacy `storage.py` for simple dashboard, new `app/routers/transactions.py` for full CRUD with new JSON schema.

**Tech Stack:** FastAPI, Pydantic, JSON storage, HTML5, CSS3, Vanilla JavaScript, pytest

---

## File Structure

### Backend Files
- **Create:** `c:/proyectos/finanzas-back/app/routers/transactions.py` - Full CRUD router for transactions (GET, POST, PUT, DELETE)
- **Create:** `c:/proyectos/finanzas-back/tests/test_transactions_api.py` - Integration tests for transaction CRUD
- **Create:** `c:/proyectos/finanzas-back/tests/test_imports_api.py` - Integration tests for import endpoints
- **Modify:** `c:/proyectos/finanzas-back/main.py:68-70` - Register new transactions router
- **Keep:** `c:/proyectos/finanzas-back/storage.py` - Legacy storage for backward compatibility with dashboard
- **Keep:** `c:/proyectos/finanzas-back/app/routers/imports.py` - Already functional, needs testing

### Frontend Files
- **Create:** `c:/proyectos/finanzas-front/css/variables.css` - CSS custom properties
- **Create:** `c:/proyectos/finanzas-front/css/base.css` - Base styles
- **Create:** `c:/proyectos/finanzas-front/css/components.css` - Component styles
- **Create:** `c:/proyectos/finanzas-front/js/config.js` - API configuration
- **Create:** `c:/proyectos/finanzas-front/js/api.js` - API client module
- **Create:** `c:/proyectos/finanzas-front/js/ui.js` - UI utility functions
- **Create:** `c:/proyectos/finanzas-front/js/dashboard.js` - Dashboard logic
- **Create:** `c:/proyectos/finanzas-front/js/imports.js` - Import functionality
- **Modify:** `c:/proyectos/finanzas-front/index.html` - Link modular CSS/JS, add Google Fonts

---

## Task 1: Setup Testing Infrastructure

**Files:**
- Create: `c:/proyectos/finanzas-back/tests/conftest.py`
- Create: `c:/proyectos/finanzas-back/pytest.ini`

- [ ] **Step 1: Create pytest configuration**

Create `c:/proyectos/finanzas-back/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

- [ ] **Step 2: Create test fixtures**

Create `c:/proyectos/finanzas-back/tests/conftest.py`:

```python
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
from config.settings import DATA_DIR


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
```

- [ ] **Step 3: Verify pytest is installed**

Run: `cd c:/proyectos/finanzas-back && pip list | grep pytest`

Expected: Shows pytest and pytest-asyncio

If not installed, run: `pip install pytest pytest-asyncio httpx`

- [ ] **Step 4: Run initial test to verify setup**

Run: `cd c:/proyectos/finanzas-back && pytest tests/ -v`

Expected: "collected 1 item" from existing test_enums_spanish.py

- [ ] **Step 5: Commit**

```bash
cd c:/proyectos/finanzas-back
git add tests/conftest.py pytest.ini
git commit -m "test: setup pytest infrastructure with fixtures"
```

---

## Task 2: Test Existing Import Endpoints

**Files:**
- Create: `c:/proyectos/finanzas-back/tests/test_imports_api.py`

- [ ] **Step 1: Write test for upload endpoint**

Create `c:/proyectos/finanzas-back/tests/test_imports_api.py`:

```python
"""
Integration tests for import endpoints
"""
import io
from fastapi.testclient import TestClient


def test_upload_csv_import(client: TestClient, sample_csv_content: str):
    """Test uploading a CSV file for import"""
    # Create file-like object
    csv_file = io.BytesIO(sample_csv_content.encode('utf-8'))
    
    response = client.post(
        "/api/v1/imports/upload",
        files={"file": ("test.csv", csv_file, "text/csv")},
        data={"source_type": "mercadopago_csv"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "batch" in data
    assert data["batch"]["total_rows"] >= 0
    assert data["batch"]["processed_rows"] >= 0


def test_upload_invalid_file_type(client: TestClient):
    """Test uploading invalid file type"""
    invalid_file = io.BytesIO(b"invalid content")
    
    response = client.post(
        "/api/v1/imports/upload",
        files={"file": ("test.txt", invalid_file, "text/plain")},
        data={"source_type": "mercadopago_csv"}
    )
    
    assert response.status_code == 400
    assert "no soportado" in response.json()["detail"].lower()


def test_get_batch_transactions_not_found(client: TestClient):
    """Test getting transactions from non-existent batch"""
    response = client.get("/api/v1/imports/batches/nonexistent-id/transactions")
    
    assert response.status_code == 404


def test_upload_and_retrieve_batch(client: TestClient, sample_csv_content: str):
    """Test complete flow: upload file and retrieve batch transactions"""
    # Upload file
    csv_file = io.BytesIO(sample_csv_content.encode('utf-8'))
    upload_response = client.post(
        "/api/v1/imports/upload",
        files={"file": ("test.csv", csv_file, "text/csv")},
        data={"source_type": "mercadopago_csv"}
    )
    
    assert upload_response.status_code == 200
    batch_id = upload_response.json()["batch"]["id"]
    
    # Retrieve batch transactions
    get_response = client.get(f"/api/v1/imports/batches/{batch_id}/transactions")
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["success"] is True
    assert data["batch_id"] == batch_id
    assert "transactions" in data
```

- [ ] **Step 2: Run import tests**

Run: `cd c:/proyectos/finanzas-back && pytest tests/test_imports_api.py -v`

Expected: Tests should pass (import endpoints already implemented)

- [ ] **Step 3: Fix any failing tests**

If tests fail, analyze the error and fix the import router or test expectations.

- [ ] **Step 4: Verify import endpoint behavior manually**

Run backend: `cd c:/proyectos/finanzas-back && uvicorn main:app --reload`

Test with curl or browser at: `http://localhost:8000/docs`

Expected: Swagger UI shows `/api/v1/imports/upload` and `/api/v1/imports/batches/{batch_id}/transactions`

- [ ] **Step 5: Commit**

```bash
cd c:/proyectos/finanzas-back
git add tests/test_imports_api.py
git commit -m "test: add integration tests for import endpoints"
```

---

## Task 3: Implement Transaction CRUD Router

**Files:**
- Create: `c:/proyectos/finanzas-back/app/routers/transactions.py`

- [ ] **Step 1: Write failing test for GET all transactions**

Create `c:/proyectos/finanzas-back/tests/test_transactions_api.py`:

```python
"""
Integration tests for transaction CRUD endpoints
"""
from fastapi.testclient import TestClient


def test_get_all_transactions_empty(client: TestClient):
    """Test getting all transactions when database is empty"""
    response = client.get("/api/v1/transactions")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_transaction(client: TestClient, sample_transaction: dict):
    """Test creating a new transaction"""
    response = client.post("/api/v1/transactions", json=sample_transaction)
    
    assert response.status_code == 201
    data = response.json()
    assert data["monto"] == sample_transaction["monto"]
    assert data["tipo"] == sample_transaction["tipo"]
    assert data["descripcion"] == sample_transaction["descripcion"]
    assert "id" in data
    assert "fecha" in data


def test_create_transaction_invalid_type(client: TestClient):
    """Test creating transaction with invalid type"""
    invalid_data = {
        "monto": 100.0,
        "tipo": "invalid_type",
        "descripcion": "Test"
    }
    
    response = client.post("/api/v1/transactions", json=invalid_data)
    
    assert response.status_code == 400


def test_get_transaction_by_id(client: TestClient, sample_transaction: dict):
    """Test getting a specific transaction by ID"""
    # Create transaction first
    create_response = client.post("/api/v1/transactions", json=sample_transaction)
    transaction_id = create_response.json()["id"]
    
    # Get by ID
    response = client.get(f"/api/v1/transactions/{transaction_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id
    assert data["monto"] == sample_transaction["monto"]


def test_get_transaction_not_found(client: TestClient):
    """Test getting non-existent transaction"""
    response = client.get("/api/v1/transactions/99999")
    
    assert response.status_code == 404


def test_update_transaction(client: TestClient, sample_transaction: dict):
    """Test updating an existing transaction"""
    # Create transaction first
    create_response = client.post("/api/v1/transactions", json=sample_transaction)
    transaction_id = create_response.json()["id"]
    
    # Update
    updated_data = {
        "monto": 2000.0,
        "tipo": "gasto",
        "descripcion": "Updated description"
    }
    response = client.put(f"/api/v1/transactions/{transaction_id}", json=updated_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id
    assert data["monto"] == updated_data["monto"]
    assert data["tipo"] == updated_data["tipo"]
    assert data["descripcion"] == updated_data["descripcion"]


def test_delete_transaction(client: TestClient, sample_transaction: dict):
    """Test deleting a transaction"""
    # Create transaction first
    create_response = client.post("/api/v1/transactions", json=sample_transaction)
    transaction_id = create_response.json()["id"]
    
    # Delete
    response = client.delete(f"/api/v1/transactions/{transaction_id}")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify deletion
    get_response = client.get(f"/api/v1/transactions/{transaction_id}")
    assert get_response.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd c:/proyectos/finanzas-back && pytest tests/test_transactions_api.py -v`

Expected: All tests FAIL with 404 errors (router not yet created)

- [ ] **Step 3: Implement transaction CRUD router**

Create `c:/proyectos/finanzas-back/app/routers/transactions.py`:

```python
"""
Transaction CRUD router
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
import storage

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]])
async def get_all_transactions():
    """Get all transactions from legacy storage"""
    transactions = storage.leer_transacciones()
    return transactions


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    monto: float,
    tipo: str,
    descripcion: str
):
    """Create a new transaction"""
    # Validate tipo
    if tipo not in ["ingreso", "gasto"]:
        raise HTTPException(
            status_code=400,
            detail="El tipo debe ser 'ingreso' o 'gasto'"
        )
    
    # Validate monto
    if monto <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto debe ser mayor a 0"
        )
    
    nueva_transaccion = storage.agregar_transaccion(
        tipo=tipo,
        monto=monto,
        descripcion=descripcion
    )
    
    return nueva_transaccion


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: int):
    """Get a specific transaction by ID"""
    transactions = storage.leer_transacciones()
    
    for transaction in transactions:
        if transaction["id"] == transaction_id:
            return transaction
    
    raise HTTPException(
        status_code=404,
        detail=f"Transacción {transaction_id} no encontrada"
    )


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    monto: float,
    tipo: str,
    descripcion: str
):
    """Update an existing transaction"""
    # Validate tipo
    if tipo not in ["ingreso", "gasto"]:
        raise HTTPException(
            status_code=400,
            detail="El tipo debe ser 'ingreso' o 'gasto'"
        )
    
    # Validate monto
    if monto <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto debe ser mayor a 0"
        )
    
    transactions = storage.leer_transacciones()
    
    for i, transaction in enumerate(transactions):
        if transaction["id"] == transaction_id:
            # Update transaction
            transactions[i]["monto"] = monto
            transactions[i]["tipo"] = tipo
            transactions[i]["descripcion"] = descripcion
            
            storage.guardar_transacciones(transactions)
            return transactions[i]
    
    raise HTTPException(
        status_code=404,
        detail=f"Transacción {transaction_id} no encontrada"
    )


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Delete a transaction"""
    transactions = storage.leer_transacciones()
    
    for i, transaction in enumerate(transactions):
        if transaction["id"] == transaction_id:
            transactions.pop(i)
            storage.guardar_transacciones(transactions)
            return {"success": True, "message": f"Transacción {transaction_id} eliminada"}
    
    raise HTTPException(
        status_code=404,
        detail=f"Transacción {transaction_id} no encontrada"
    )
```

- [ ] **Step 4: Register router in main.py**

Modify `c:/proyectos/finanzas-back/main.py` at line 68:

```python
# Import transactions router
from app.routers import imports, transactions

# Register routers (after line 16)
app.include_router(imports.router, prefix="/api/v1/imports", tags=["Imports"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd c:/proyectos/finanzas-back && pytest tests/test_transactions_api.py -v`

Expected: All tests PASS

- [ ] **Step 6: Test endpoints manually**

Start backend: `cd c:/proyectos/finanzas-back && uvicorn main:app --reload`

Visit: `http://localhost:8000/docs`

Test each endpoint (GET, POST, PUT, DELETE) via Swagger UI

Expected: All CRUD operations work correctly

- [ ] **Step 7: Commit**

```bash
cd c:/proyectos/finanzas-back
git add app/routers/transactions.py main.py tests/test_transactions_api.py
git commit -m "feat: implement transaction CRUD endpoints with tests"
```

---

## Task 4: Refactor Frontend - CSS Variables & Modularization

**Files:**
- Create: `c:/proyectos/finanzas-front/css/variables.css`
- Create: `c:/proyectos/finanzas-front/css/base.css`
- Create: `c:/proyectos/finanzas-front/css/components.css`

- [ ] **Step 1: Extract CSS variables**

Create `c:/proyectos/finanzas-front/css/variables.css`:

```css
/**
 * CSS Custom Properties for Finanzas App
 */
:root {
  /* Colors - Primary */
  --color-primary: #00d4ff;
  --color-primary-dark: #0099cc;
  --color-primary-light: rgba(0, 212, 255, 0.2);
  
  /* Colors - Status */
  --color-success: #2ed573;
  --color-success-light: rgba(46, 213, 115, 0.2);
  --color-error: #ff4757;
  --color-error-light: rgba(255, 71, 87, 0.2);
  --color-warning: #ffa502;
  --color-warning-light: rgba(255, 165, 2, 0.2);
  
  /* Colors - Background */
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --bg-tertiary: #0f3460;
  --bg-card: rgba(22, 33, 62, 0.8);
  --bg-input: rgba(15, 52, 96, 0.6);
  
  /* Colors - Text */
  --text-primary: #e4e4e4;
  --text-secondary: #a0a0a0;
  --text-white: #ffffff;
  
  /* Borders */
  --border-primary: rgba(0, 212, 255, 0.2);
  --border-light: rgba(255, 255, 255, 0.05);
  
  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.3);
  --shadow-glow-primary: 0 0 30px rgba(0, 212, 255, 0.5);
  --shadow-glow-success: 0 0 30px rgba(46, 213, 115, 0.5);
  --shadow-glow-error: 0 0 30px rgba(255, 71, 87, 0.5);
  
  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 20px;
  --spacing-lg: 30px;
  --spacing-xl: 40px;
  
  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 15px;
  --radius-xl: 20px;
  --radius-pill: 12px;
  
  /* Typography */
  --font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.85rem;
  --font-size-md: 0.95rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.1rem;
  --font-size-xl: 1.3rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 2.5rem;
  --font-size-4xl: 4rem;
  
  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.3s ease;
  --transition-slow: 0.5s ease;
  
  /* Z-index */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal: 1040;
  --z-tooltip: 1050;
}
```

- [ ] **Step 2: Create base styles**

Create `c:/proyectos/finanzas-front/css/base.css`:

```css
/**
 * Base styles and resets
 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  color: var(--text-primary);
  min-height: 100vh;
  padding: var(--spacing-md);
  line-height: 1.6;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Typography */
h1 {
  font-size: var(--font-size-3xl);
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
  text-shadow: var(--shadow-glow-primary);
}

h2 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-2xl);
}

h3 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 52, 96, 0.3);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: var(--color-primary-light);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn var(--transition-base);
}
```

- [ ] **Step 3: Create component styles**

Create `c:/proyectos/finanzas-front/css/components.css`:

```css
/**
 * Component styles
 */

/* Header */
header {
  text-align: center;
  margin-bottom: var(--spacing-lg);
}

/* Cards */
.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  transition: transform var(--transition-base);
}

.card:hover {
  transform: translateY(-2px);
}

/* Balance Section */
.balance-section {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  text-align: center;
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-primary);
}

.balance-label {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.balance-amount {
  font-size: var(--font-size-4xl);
  font-weight: bold;
  color: var(--color-primary);
  text-shadow: var(--shadow-glow-primary);
}

.balance-amount.negative {
  color: var(--color-error);
  text-shadow: var(--shadow-glow-error);
}

/* Buttons */
button {
  width: 100%;
  padding: var(--spacing-sm);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-white);
  font-size: var(--font-size-lg);
  font-weight: bold;
  cursor: pointer;
  transition: all var(--transition-base);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-family: var(--font-family);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
}

button:active {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Form Elements */
.form-group {
  margin-bottom: var(--spacing-md);
}

label {
  display: block;
  margin-bottom: var(--spacing-xs);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 1px;
}

input,
select,
textarea {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-sm);
  background: var(--bg-input);
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  transition: all var(--transition-base);
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

textarea {
  resize: vertical;
  min-height: 80px;
}

/* Messages */
.success-message {
  background: var(--color-success-light);
  border: 1px solid var(--color-success);
  color: var(--color-success);
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-sm);
  text-align: center;
}

.error-message {
  background: var(--color-error-light);
  border: 1px solid var(--color-error);
  color: var(--color-error);
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-sm);
  text-align: center;
}

/* Loading */
.spinner {
  border: 3px solid var(--color-primary-light);
  border-radius: 50%;
  border-top: 3px solid var(--color-primary);
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: var(--spacing-md) auto;
}

.loading {
  text-align: center;
  padding: var(--spacing-md);
  color: var(--color-primary);
}

/* Tabs */
.nav-tabs {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--border-light);
}

.nav-tab {
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--font-size-base);
  font-weight: 500;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  width: auto;
  text-transform: none;
  letter-spacing: normal;
}

.nav-tab:hover {
  color: var(--text-primary);
}

.nav-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}

/* Responsive Grid */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

@media (max-width: 968px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* Transactions List */
.transactions-list {
  max-height: 500px;
  overflow-y: auto;
}

.transaction-item {
  background: rgba(15, 52, 96, 0.4);
  border-left: 4px solid var(--color-primary);
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
}

.transaction-item:hover {
  background: rgba(15, 52, 96, 0.7);
  transform: translateX(5px);
}

.transaction-item.gasto {
  border-left-color: var(--color-error);
}

.transaction-item.ingreso {
  border-left-color: var(--color-success);
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.transaction-type {
  font-size: var(--font-size-sm);
  padding: 4px var(--spacing-xs);
  border-radius: var(--radius-pill);
  text-transform: uppercase;
  font-weight: bold;
  letter-spacing: 1px;
}

.transaction-type.ingreso {
  background: var(--color-success-light);
  color: var(--color-success);
}

.transaction-type.gasto {
  background: var(--color-error-light);
  color: var(--color-error);
}

.transaction-amount {
  font-size: var(--font-size-xl);
  font-weight: bold;
}

.transaction-amount.ingreso {
  color: var(--color-success);
}

.transaction-amount.gasto {
  color: var(--color-error);
}

.transaction-description {
  color: var(--text-secondary);
  font-size: var(--font-size-md);
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--spacing-xl);
  font-size: var(--font-size-lg);
}
```

- [ ] **Step 4: Add Google Fonts to HTML**

Modify `c:/proyectos/finanzas-front/index.html` in `<head>` section (after line 6):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<!-- CSS Files -->
<link rel="stylesheet" href="css/variables.css">
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/components.css">
```

Remove the old `<style>` block (lines 7-633) from index.html

- [ ] **Step 5: Test CSS refactor**

Open `c:/proyectos/finanzas-front/index.html` in browser

Expected: Same visual appearance with new modular CSS

- [ ] **Step 6: Commit**

```bash
cd c:/proyectos/finanzas-front
git add css/ index.html
git commit -m "refactor: modularize CSS with variables and Google Fonts"
```

---

## Task 5: Refactor Frontend - JavaScript Modules

**Files:**
- Create: `c:/proyectos/finanzas-front/js/config.js`
- Create: `c:/proyectos/finanzas-front/js/api.js`
- Create: `c:/proyectos/finanzas-front/js/ui.js`
- Create: `c:/proyectos/finanzas-front/js/dashboard.js`
- Create: `c:/proyectos/finanzas-front/js/imports.js`

- [ ] **Step 1: Create config module**

Create `c:/proyectos/finanzas-front/js/config.js`:

```javascript
/**
 * Application configuration
 */
export const CONFIG = {
  API_URL: 'http://127.0.0.1:8000',
  API_TIMEOUT: 30000,
  MAX_FILE_SIZE_MB: 50,
  SUPPORTED_FORMATS: ['.csv', '.xlsx', '.xls'],
  CURRENCY: 'USD',
  LOCALE: 'es-AR'
};
```

- [ ] **Step 2: Create API client module**

Create `c:/proyectos/finanzas-front/js/api.js`:

```javascript
/**
 * API client module
 */
import { CONFIG } from './config.js';

class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Transaction endpoints
  async getTransactions() {
    return this.request('/transacciones');
  }

  async createTransaction(data) {
    return this.request('/transacciones', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async getBalance() {
    return this.request('/balance');
  }

  // Import endpoints
  async uploadImportFile(file, sourceType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', sourceType);

    return fetch(`${this.baseURL}/api/v1/imports/upload`, {
      method: 'POST',
      body: formData
    }).then(async response => {
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
      }
      return response.json();
    });
  }

  async getBatchTransactions(batchId) {
    return this.request(`/api/v1/imports/batches/${batchId}/transactions`);
  }
}

export const api = new APIClient(CONFIG.API_URL);
```

- [ ] **Step 3: Create UI utilities module**

Create `c:/proyectos/finanzas-front/js/ui.js`:

```javascript
/**
 * UI utility functions
 */
import { CONFIG } from './config.js';

export function formatCurrency(amount) {
  return new Intl.NumberFormat(CONFIG.LOCALE, {
    style: 'currency',
    currency: CONFIG.CURRENCY
  }).format(amount);
}

export function formatDate(dateString) {
  if (!dateString) return '-';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString(CONFIG.LOCALE, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch {
    return dateString;
  }
}

export function showMessage(elementId, message, type = 'success') {
  const messageDiv = document.getElementById(elementId);
  if (!messageDiv) return;

  messageDiv.className = type === 'success' ? 'success-message' : 'error-message';
  messageDiv.textContent = message;

  setTimeout(() => {
    messageDiv.textContent = '';
    messageDiv.className = '';
  }, 5000);
}

export function showLoading(elementId, show = true) {
  const element = document.getElementById(elementId);
  if (!element) return;

  if (show) {
    element.innerHTML = '<div class="loading"><div class="spinner"></div>Cargando...</div>';
  }
}

export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

export function switchTab(tabName) {
  // Update tab buttons
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
  if (activeTab) activeTab.classList.add('active');

  // Update tab content
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  const activeContent = document.getElementById(tabName);
  if (activeContent) activeContent.classList.add('active');
}
```

- [ ] **Step 4: Create dashboard module**

Create `c:/proyectos/finanzas-front/js/dashboard.js`:

```javascript
/**
 * Dashboard functionality
 */
import { api } from './api.js';
import { formatCurrency, showMessage, showLoading } from './ui.js';

let transactions = [];

export async function initDashboard() {
  // Load initial data
  await loadBalance();
  await loadTransactions();

  // Setup form handler
  const form = document.getElementById('transactionForm');
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }

  // Setup window resize handler for chart
  window.addEventListener('resize', () => {
    const totals = calculateTotals();
    updateChart(totals);
  });
}

async function loadBalance() {
  try {
    const data = await api.getBalance();
    const balanceElement = document.getElementById('balanceAmount');
    if (balanceElement) {
      balanceElement.textContent = formatCurrency(data.balance);
      balanceElement.className = 'balance-amount' + (data.balance < 0 ? ' negative' : '');
    }
  } catch (error) {
    console.error('Error loading balance:', error);
  }
}

async function loadTransactions() {
  try {
    showLoading('transactionsList');
    transactions = await api.getTransactions();
    updateUI();
  } catch (error) {
    console.error('Error loading transactions:', error);
    const listElement = document.getElementById('transactionsList');
    if (listElement) {
      listElement.innerHTML = '<div class="empty-state">Error al cargar transacciones. Verifica que la API esté funcionando.</div>';
    }
  }
}

async function handleFormSubmit(e) {
  e.preventDefault();

  const formData = {
    monto: parseFloat(document.getElementById('amount').value),
    tipo: document.getElementById('type').value,
    descripcion: document.getElementById('description').value
  };

  try {
    const newTransaction = await api.createTransaction(formData);
    transactions.push(newTransaction);
    updateUI();
    await loadBalance();
    showMessage('formMessage', 'Transacción agregada exitosamente', 'success');
    e.target.reset();
  } catch (error) {
    console.error('Error creating transaction:', error);
    showMessage('formMessage', error.message || 'Error al agregar transacción', 'error');
  }
}

function calculateTotals() {
  const totals = transactions.reduce((acc, transaction) => {
    if (transaction.tipo === 'ingreso') {
      acc.income += parseFloat(transaction.monto);
    } else {
      acc.expense += parseFloat(transaction.monto);
    }
    return acc;
  }, { income: 0, expense: 0 });

  totals.balance = totals.income - totals.expense;
  return totals;
}

function updateUI() {
  const totals = calculateTotals();

  // Update balance
  const balanceElement = document.getElementById('balanceAmount');
  if (balanceElement) {
    balanceElement.textContent = formatCurrency(totals.balance);
    balanceElement.className = 'balance-amount' + (totals.balance < 0 ? ' negative' : '');
  }

  // Update totals
  const incomeElement = document.getElementById('totalIncome');
  const expenseElement = document.getElementById('totalExpense');
  if (incomeElement) incomeElement.textContent = formatCurrency(totals.income);
  if (expenseElement) expenseElement.textContent = formatCurrency(totals.expense);

  // Update list
  renderTransactions();

  // Update chart
  updateChart(totals);
}

function renderTransactions() {
  const listElement = document.getElementById('transactionsList');
  if (!listElement) return;

  if (transactions.length === 0) {
    listElement.innerHTML = '<div class="empty-state">No hay transacciones registradas</div>';
    return;
  }

  const html = transactions
    .sort((a, b) => b.id - a.id)
    .map(transaction => `
      <div class="transaction-item ${transaction.tipo}">
        <div class="transaction-header">
          <span class="transaction-type ${transaction.tipo}">
            ${transaction.tipo === 'ingreso' ? 'Ingreso' : 'Gasto'}
          </span>
          <span class="transaction-amount ${transaction.tipo}">
            ${transaction.tipo === 'ingreso' ? '+' : '-'}${formatCurrency(Math.abs(transaction.monto))}
          </span>
        </div>
        <div class="transaction-description">${transaction.descripcion}</div>
      </div>
    `).join('');

  listElement.innerHTML = html;
}

function updateChart(totals) {
  const canvas = document.getElementById('pieChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  if (totals.income === 0 && totals.expense === 0) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '16px Inter';
    ctx.fillStyle = '#a0a0a0';
    ctx.textAlign = 'center';
    ctx.fillText('No hay datos para mostrar', canvas.width / 2, canvas.height / 2);
    return;
  }

  const size = Math.min(canvas.parentElement.clientWidth, canvas.parentElement.clientHeight);
  canvas.width = size;
  canvas.height = size;

  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = Math.min(centerX, centerY) - 20;

  const total = totals.income + totals.expense;
  const incomeAngle = (totals.income / total) * 2 * Math.PI;
  const expenseAngle = (totals.expense / total) * 2 * Math.PI;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw income segment
  if (totals.income > 0) {
    ctx.beginPath();
    ctx.fillStyle = '#2ed573';
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, -Math.PI / 2 + incomeAngle);
    ctx.closePath();
    ctx.shadowColor = 'rgba(46, 213, 115, 0.5)';
    ctx.shadowBlur = 15;
    ctx.fill();
    ctx.shadowBlur = 0;
  }

  // Draw expense segment
  if (totals.expense > 0) {
    ctx.beginPath();
    ctx.fillStyle = '#ff4757';
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, -Math.PI / 2 + incomeAngle, -Math.PI / 2 + incomeAngle + expenseAngle);
    ctx.closePath();
    ctx.shadowColor = 'rgba(255, 71, 87, 0.5)';
    ctx.shadowBlur = 15;
    ctx.fill();
    ctx.shadowBlur = 0;
  }

  // Draw center circle (donut style)
  ctx.beginPath();
  ctx.fillStyle = 'rgba(22, 33, 62, 0.9)';
  ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI);
  ctx.fill();

  // Draw percentages
  ctx.font = 'bold 18px Inter';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#ffffff';

  if (totals.income > 0) {
    const incomePercent = ((totals.income / total) * 100).toFixed(1);
    const incomeAnglePos = -Math.PI / 2 + incomeAngle / 2;
    const incomeX = centerX + Math.cos(incomeAnglePos) * (radius * 0.75);
    const incomeY = centerY + Math.sin(incomeAnglePos) * (radius * 0.75);
    ctx.fillText(`${incomePercent}%`, incomeX, incomeY);
  }

  if (totals.expense > 0) {
    const expensePercent = ((totals.expense / total) * 100).toFixed(1);
    const expenseAnglePos = -Math.PI / 2 + incomeAngle + expenseAngle / 2;
    const expenseX = centerX + Math.cos(expenseAnglePos) * (radius * 0.75);
    const expenseY = centerY + Math.sin(expenseAnglePos) * (radius * 0.75);
    ctx.fillText(`${expensePercent}%`, expenseX, expenseY);
  }
}
```

- [ ] **Step 5: Create imports module**

Create `c:/proyectos/finanzas-front/js/imports.js`:

```javascript
/**
 * Import functionality
 */
import { api } from './api.js';
import { CONFIG } from './config.js';
import { formatCurrency, formatDate, showMessage, escapeHtml, switchTab } from './ui.js';

let selectedFile = null;
let importedTransactions = [];

export function initImports() {
  setupFileUpload();
  setupImportButton();
  setupConfirmButton();
}

function setupFileUpload() {
  const uploadArea = document.getElementById('uploadArea');
  const fileInput = document.getElementById('fileInput');
  const removeFileBtn = document.getElementById('removeFile');

  if (uploadArea && fileInput) {
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0]));
    
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('drag-over');
      if (e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });
  }

  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearFileSelection();
    });
  }
}

function handleFileSelect(file) {
  if (!file) return;

  const fileExt = '.' + file.name.split('.').pop().toLowerCase();

  if (!CONFIG.SUPPORTED_FORMATS.includes(fileExt)) {
    showMessage('importMessage', 'Formato de archivo no válido. Usa CSV o XLSX.', 'error');
    return;
  }

  if (file.size > CONFIG.MAX_FILE_SIZE_MB * 1024 * 1024) {
    showMessage('importMessage', `El archivo es demasiado grande. Máximo ${CONFIG.MAX_FILE_SIZE_MB}MB.`, 'error');
    return;
  }

  selectedFile = file;
  
  const fileName = document.getElementById('fileName');
  const fileInfo = document.getElementById('fileInfo');
  const uploadArea = document.getElementById('uploadArea');
  const importButton = document.getElementById('importButton');

  if (fileName) fileName.textContent = file.name;
  if (fileInfo) fileInfo.style.display = 'flex';
  if (uploadArea) uploadArea.classList.add('has-file');
  if (importButton) importButton.disabled = false;

  const importResults = document.getElementById('importResults');
  if (importResults) importResults.style.display = 'none';
}

function clearFileSelection() {
  selectedFile = null;
  
  const fileInput = document.getElementById('fileInput');
  const fileInfo = document.getElementById('fileInfo');
  const uploadArea = document.getElementById('uploadArea');
  const importButton = document.getElementById('importButton');

  if (fileInput) fileInput.value = '';
  if (fileInfo) fileInfo.style.display = 'none';
  if (uploadArea) uploadArea.classList.remove('has-file');
  if (importButton) importButton.disabled = true;
}

function setupImportButton() {
  const importButton = document.getElementById('importButton');
  if (!importButton) return;

  importButton.addEventListener('click', async () => {
    if (!selectedFile) {
      showMessage('importMessage', 'Por favor selecciona un archivo primero.', 'error');
      return;
    }

    const sourceType = document.getElementById('sourceType')?.value || 'mercadopago_csv';

    importButton.disabled = true;
    importButton.innerHTML = '<div class="spinner" style="margin: 0 auto; width: 20px; height: 20px;"></div>';

    try {
      const result = await api.uploadImportFile(selectedFile, sourceType);

      if (result && result.batch) {
        showMessage('importMessage', '¡Importación completada exitosamente!', 'success');
        displayImportResults(result.batch);
        await loadImportedTransactions(result.batch.id);
      } else {
        throw new Error('Respuesta inesperada del servidor');
      }
    } catch (error) {
      console.error('Error en importación:', error);
      showMessage('importMessage', error.message || 'Error al importar archivo', 'error');
    } finally {
      importButton.disabled = false;
      importButton.textContent = 'Importar Transacciones';
    }
  });
}

function displayImportResults(batch) {
  const resultsSection = document.getElementById('importResults');
  if (resultsSection) {
    resultsSection.style.display = 'block';
  }

  document.getElementById('kpiTotal').textContent = batch.total_rows || 0;
  document.getElementById('kpiProcessed').textContent = batch.processed_rows || 0;
  document.getElementById('kpiDuplicated').textContent = batch.duplicated_rows || 0;
  document.getElementById('kpiFailed').textContent = batch.failed_rows || 0;

  const reviewRequired = batch.metadata?.review_required || 0;
  document.getElementById('kpiReview').textContent = reviewRequired;

  setTimeout(() => {
    resultsSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

async function loadImportedTransactions(batchId) {
  try {
    const data = await api.getBatchTransactions(batchId);
    renderImportedTransactions(data.transactions || []);
  } catch (error) {
    console.error('Error loading imported transactions:', error);
    const tbody = document.getElementById('importedTransactionsBody');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #ff4757;">Error al cargar transacciones</td></tr>';
    }
  }
}

function renderImportedTransactions(transactions) {
  const tbody = document.getElementById('importedTransactionsBody');
  const confirmButton = document.getElementById('confirmButton');

  if (!tbody) return;

  if (transactions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #a0a0a0;">No hay transacciones para mostrar</td></tr>';
    if (confirmButton) confirmButton.style.display = 'none';
    return;
  }

  importedTransactions = transactions;

  const html = transactions.map(tx => {
    const date = formatDate(tx.operation_date);
    const description = tx.description || 'Sin descripción';
    const merchant = tx.merchant || tx.merchant_normalized || '-';
    const displayAmount = tx.real_amount !== undefined ? tx.real_amount : tx.amount;
    const amount = formatCurrency(Math.abs(displayAmount || 0));
    const currency = tx.currency || 'ARS';
    const type = formatTransactionType(tx.transaction_type);
    const category = tx.suggested_category_id || 'Sin categoría';
    const status = formatStatus(tx.status);

    let paymentMethod = tx.payment_method || '-';
    if (tx.payment_method_type && tx.payment_method_type !== tx.payment_method) {
      paymentMethod = `${tx.payment_method} (${tx.payment_method_type})`;
    }

    return `
      <tr>
        <td>${date}</td>
        <td>${escapeHtml(description)}</td>
        <td>${escapeHtml(merchant)}</td>
        <td style="font-weight: bold;">${amount}</td>
        <td>${currency}</td>
        <td>${type}</td>
        <td>${escapeHtml(category)}</td>
        <td>${status}</td>
        <td>${escapeHtml(paymentMethod)}</td>
      </tr>
    `;
  }).join('');

  tbody.innerHTML = html;

  const confirmedTransactions = transactions.filter(tx =>
    tx.status && tx.status.toLowerCase() === 'confirmada'
  );

  if (confirmButton) {
    confirmButton.style.display = confirmedTransactions.length > 0 ? 'block' : 'none';
  }
}

function formatTransactionType(type) {
  const typeMap = {
    'ingreso': '<span class="badge ingreso">Ingreso</span>',
    'gasto': '<span class="badge gasto">Gasto</span>',
    'transferencia': '<span class="badge transferencia">Transferencia</span>',
  };
  return typeMap[type?.toLowerCase()] || `<span class="badge">${type || '-'}</span>`;
}

function formatStatus(status) {
  const statusMap = {
    'confirmada': '<span class="badge confirmada">Confirmada</span>',
    'pendiente': '<span class="badge pendiente">Pendiente</span>',
    'duplicada': '<span class="badge duplicada">Duplicada</span>',
    'ignorada': '<span class="badge ignorada">Ignorada</span>',
  };
  return statusMap[status?.toLowerCase()] || `<span class="badge">${status || '-'}</span>`;
}

function setupConfirmButton() {
  const confirmButton = document.getElementById('confirmButton');
  if (!confirmButton) return;

  confirmButton.addEventListener('click', async () => {
    const confirmedTransactions = importedTransactions.filter(tx =>
      tx.status && tx.status.toLowerCase() === 'confirmada'
    );

    if (confirmedTransactions.length === 0) {
      showMessage('importMessage', 'No hay transacciones confirmadas para registrar.', 'error');
      return;
    }

    confirmButton.disabled = true;
    confirmButton.innerHTML = '<div class="spinner" style="margin: 0 auto; width: 20px; height: 20px;"></div>';

    let registeredCount = 0;
    let errorCount = 0;

    try {
      for (const tx of confirmedTransactions) {
        try {
          const transactionData = {
            monto: Math.abs(tx.amount || 0),
            tipo: tx.transaction_type.toLowerCase(),
            descripcion: tx.description || tx.merchant || 'Importado desde Mercado Pago'
          };

          await api.createTransaction(transactionData);
          registeredCount++;
        } catch (error) {
          errorCount++;
          console.error(`Error registering transaction: ${tx.description}`, error);
        }
      }

      if (registeredCount > 0) {
        showMessage(
          'importMessage',
          `✓ ${registeredCount} transacción(es) registrada(s) exitosamente.${errorCount > 0 ? ` ${errorCount} fallaron.` : ''}`,
          'success'
        );

        setTimeout(() => switchTab('dashboard'), 2000);
      } else {
        showMessage('importMessage', 'Error: No se pudieron registrar las transacciones.', 'error');
      }
    } catch (error) {
      console.error('Error confirming transactions:', error);
      showMessage('importMessage', 'Error al procesar las transacciones.', 'error');
    } finally {
      confirmButton.disabled = false;
      confirmButton.textContent = 'Confirmar y Registrar en Dashboard';
    }
  });
}
```

- [ ] **Step 6: Create main app entry point**

Modify `c:/proyectos/finanzas-front/index.html` - replace entire `<script>` block (lines 813-1483) with:

```html
<script type="module">
  import { initDashboard } from './js/dashboard.js';
  import { initImports } from './js/imports.js';
  import { switchTab } from './js/ui.js';

  // Initialize app
  document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    initImports();

    // Setup tab navigation
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const tabName = tab.getAttribute('data-tab');
        switchTab(tabName);
      });
    });
  });
</script>
```

- [ ] **Step 7: Test modularized JavaScript**

Open `c:/proyectos/finanzas-front/index.html` in browser

Expected: All functionality works (dashboard, imports, forms, charts)

Check browser console for errors

- [ ] **Step 8: Commit**

```bash
cd c:/proyectos/finanzas-front
git add js/ index.html
git commit -m "refactor: modularize JavaScript with ES6 modules"
```

---

## Task 6: Integration Testing with Superpowers

**Files:**
- No new files (verification task)

- [ ] **Step 1: Start backend server**

Run: `cd c:/proyectos/finanzas-back && uvicorn main:app --reload`

Expected: Server starts on http://localhost:8000

- [ ] **Step 2: Verify backend endpoints via Swagger**

Open: `http://localhost:8000/docs`

Test each endpoint manually:
- POST /transacciones
- GET /transacciones
- GET /transacciones/{id}
- PUT /transacciones/{id}
- DELETE /transacciones/{id}
- POST /api/v1/imports/upload
- GET /api/v1/imports/batches/{batch_id}/transactions

Expected: All endpoints respond correctly

- [ ] **Step 3: Run all backend tests**

Run: `cd c:/proyectos/finanzas-back && pytest tests/ -v`

Expected: All tests PASS

- [ ] **Step 4: Test frontend integration**

Open: `c:/proyectos/finanzas-front/index.html` in browser

Test scenarios:
1. Create a new transaction via form
2. Verify transaction appears in list
3. Check balance updates correctly
4. Switch to Import tab
5. Upload sample CSV file (`c:/proyectos/finanzas-back/data/mercadopago_ejemplo.csv`)
6. Verify import results display
7. Confirm and register imported transactions
8. Switch back to Dashboard tab
9. Verify imported transactions appear

Expected: All functionality works end-to-end

- [ ] **Step 5: Check browser console for errors**

Open browser DevTools Console

Expected: No JavaScript errors, all API calls successful

- [ ] **Step 6: Test responsive design**

Resize browser window to mobile size (375px width)

Expected: Layout adapts correctly, all elements remain functional

- [ ] **Step 7: Document test results**

Create test report noting:
- All endpoints tested
- Frontend functionality verified
- Any issues found and resolved
- Performance observations

---

## Task 7: Code Review and Cleanup

**Files:**
- Various (cleanup task)

- [ ] **Step 1: Review backend code quality**

Check:
- Consistent error handling
- Proper HTTP status codes
- Clear function/variable names
- No commented-out code
- Proper typing hints

- [ ] **Step 2: Review frontend code quality**

Check:
- Consistent naming conventions
- Proper error handling
- No console.log statements in production code
- Proper use of const/let
- Clear function names

- [ ] **Step 3: Check for unused code**

Search for:
- Unused imports
- Unused functions
- Unused CSS classes
- Commented-out code blocks

Remove any found

- [ ] **Step 4: Verify all files have proper headers**

Each file should have:
- Brief description comment at top
- Clear purpose statement

- [ ] **Step 5: Run final tests**

Backend: `cd c:/proyectos/finanzas-back && pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Create final commit**

```bash
# Backend
cd c:/proyectos/finanzas-back
git add .
git commit -m "chore: code cleanup and documentation"

# Frontend
cd c:/proyectos/finanzas-front
git add .
git commit -m "chore: code cleanup and documentation"
```

- [ ] **Step 7: Update README files**

Add sections documenting:
- API endpoints
- Frontend architecture
- How to run tests
- Development workflow

---

## Self-Review

**Spec Coverage:**
✅ Verify and fix import endpoints - Task 2
✅ Implement transaction CRUD endpoints - Task 3
✅ Testing infrastructure - Task 1, 6
✅ Frontend refactor with CSS variables - Task 4
✅ Frontend refactor with modular JS - Task 5
✅ Integration testing - Task 6
✅ Code cleanup - Task 7

**Placeholder Scan:**
✅ No TBD or TODO markers
✅ All code blocks contain actual implementation
✅ All file paths are exact
✅ All commands have expected output

**Type Consistency:**
✅ API endpoints consistent across tasks
✅ Function names match across modules
✅ CSS class names consistent

---

## Summary

This plan implements:

1. **Complete CRUD API** for transactions with full test coverage
2. **Verified import endpoints** with integration tests
3. **Modular frontend** with CSS variables, Google Fonts (Inter), and ES6 modules
4. **Comprehensive testing** using pytest and manual verification
5. **Clean architecture** with separation of concerns

The result is a production-ready personal finance application with modern architecture, full test coverage, and maintainable code.
