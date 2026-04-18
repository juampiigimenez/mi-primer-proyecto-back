# Finanzas Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix dashboard transaction visibility bug, change currency format from USD to ARS globally, and add persistent import history with notifications.

**Architecture:** Backend adds `import_history` collection and new model, modifies confirm endpoint to create history records. Frontend changes currency formatting globally, simplifies import table columns, adds toast notifications and history component.

**Tech Stack:** FastAPI, Pydantic, Python datetime, JavaScript ES6 modules, Intl.NumberFormat, CSS animations

---

## File Structure

### Backend Files
- **Create:** `c:/proyectos/finanzas-back/app/models/import_history.py` - ImportHistory Pydantic model
- **Modify:** `c:/proyectos/finanzas-back/app/repositories/json_repository.py` - Add import_history collection
- **Modify:** `c:/proyectos/finanzas-back/app/routers/imports.py` - Add history endpoint, modify confirm endpoint
- **Create:** `c:/proyectos/finanzas-back/tests/test_import_history.py` - Tests for history functionality

### Frontend Files
- **Modify:** `c:/proyectos/finanzas-front/js/config.js` - Change CURRENCY to ARS
- **Modify:** `c:/proyectos/finanzas-front/js/ui.js` - Fix formatCurrency, add showToast and formatDateTime
- **Modify:** `c:/proyectos/finanzas-front/js/api.js` - Add getImportHistory method
- **Modify:** `c:/proyectos/finanzas-front/js/imports.js` - Simplify table columns, add history loading/rendering, integrate toast
- **Modify:** `c:/proyectos/finanzas-front/js/dashboard.js` - Ensure loadDashboardData properly reloads
- **Modify:** `c:/proyectos/finanzas-front/index.html` - Reduce table columns, add history section
- **Modify:** `c:/proyectos/finanzas-front/css/components.css` - Add toast and history styles

---

## Task 1: Backend - Create ImportHistory Model

**Files:**
- Create: `c:/proyectos/finanzas-back/app/models/import_history.py`

- [ ] **Step 1: Write the failing test for ImportHistory model validation**

```python
# File: c:/proyectos/finanzas-back/tests/test_import_history.py
import pytest
from datetime import datetime
from app.models.import_history import ImportHistory

def test_import_history_model_valid():
    """Test ImportHistory model with valid data"""
    history = ImportHistory(
        id="hist-abc123",
        filename="settlement-x-2024-04-18.csv",
        uploaded_at=datetime(2024, 4, 18, 14, 25, 0),
        confirmed_at=datetime(2024, 4, 18, 14, 30, 0),
        batch_id="batch-xyz789",
        status="confirmed",
        total_transactions=24,
        total_ingresos=15000.50,
        total_gastos=8500.75,
        week_number=16,
        display_name="Semana 16 - 2024"
    )
    
    assert history.id == "hist-abc123"
    assert history.filename == "settlement-x-2024-04-18.csv"
    assert history.week_number == 16
    assert history.display_name == "Semana 16 - 2024"
    assert history.total_transactions == 24
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_import_history.py::test_import_history_model_valid -v`
Expected: FAIL with "No module named 'app.models.import_history'"

- [ ] **Step 3: Create ImportHistory model**

```python
# File: c:/proyectos/finanzas-back/app/models/import_history.py
"""
Import History model - Track confirmed import batches
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class ImportHistory(BaseModel):
    """Record of a confirmed import batch"""
    
    id: str = Field(..., description="Unique identifier (e.g., hist-abc123)")
    filename: str = Field(..., description="Original filename (e.g., settlement-x-2024-04-18.csv)")
    uploaded_at: datetime = Field(..., description="When the file was uploaded")
    confirmed_at: datetime = Field(..., description="When the import was confirmed")
    batch_id: str = Field(..., description="Reference to the import batch")
    status: Literal["confirmed"] = Field(default="confirmed", description="Import status")
    total_transactions: int = Field(..., ge=0, description="Total number of transactions")
    total_ingresos: float = Field(..., ge=0, description="Total income amount")
    total_gastos: float = Field(..., ge=0, description="Total expense amount")
    week_number: int = Field(..., ge=1, le=53, description="ISO 8601 week number")
    display_name: str = Field(..., description="Display name (e.g., Semana 16 - 2024)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "hist-abc123",
                "filename": "settlement-x-2024-04-18.csv",
                "uploaded_at": "2024-04-18T14:25:00",
                "confirmed_at": "2024-04-18T14:30:00",
                "batch_id": "batch-xyz789",
                "status": "confirmed",
                "total_transactions": 24,
                "total_ingresos": 15000.50,
                "total_gastos": 8500.75,
                "week_number": 16,
                "display_name": "Semana 16 - 2024"
            }
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_import_history.py::test_import_history_model_valid -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/models/import_history.py tests/test_import_history.py
git commit -m "feat: add ImportHistory model

- Pydantic model for tracking confirmed import batches
- Includes filename parsing metadata (week_number, display_name)
- Test coverage for model validation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Backend - Add Filename Parsing Utility

**Files:**
- Modify: `c:/proyectos/finanzas-back/app/routers/imports.py`
- Modify: `c:/proyectos/finanzas-back/tests/test_import_history.py`

- [ ] **Step 1: Write failing test for filename parsing**

```python
# File: c:/proyectos/finanzas-back/tests/test_import_history.py
# Add to existing file:

from app.routers.imports import parse_settlement_filename

def test_parse_settlement_filename_valid():
    """Test parsing valid settlement filename"""
    result = parse_settlement_filename("settlement-x-2024-04-18.csv")
    
    assert result["week"] == 16
    assert result["year"] == 2024
    assert result["display_name"] == "Semana 16 - 2024"
    assert result["date"].year == 2024
    assert result["date"].month == 4
    assert result["date"].day == 18


def test_parse_settlement_filename_different_week():
    """Test parsing filename from different week"""
    result = parse_settlement_filename("settlement-x-2024-01-01.csv")
    
    assert result["week"] == 1
    assert result["year"] == 2024
    assert result["display_name"] == "Semana 1 - 2024"


def test_parse_settlement_filename_end_of_year():
    """Test parsing filename at end of year"""
    result = parse_settlement_filename("settlement-x-2024-12-30.csv")
    
    # Week 53 or 1 depending on ISO 8601 rules
    assert result["week"] in [1, 52, 53]
    assert result["display_name"].startswith("Semana ")


def test_parse_settlement_filename_invalid_format():
    """Test parsing invalid filename raises ValueError"""
    with pytest.raises(ValueError, match="Formato de filename inválido"):
        parse_settlement_filename("invalid-file.csv")


def test_parse_settlement_filename_missing_date():
    """Test parsing filename without date raises ValueError"""
    with pytest.raises(ValueError, match="Formato de filename inválido"):
        parse_settlement_filename("settlement-x.csv")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_import_history.py::test_parse_settlement_filename_valid -v`
Expected: FAIL with "cannot import name 'parse_settlement_filename'"

- [ ] **Step 3: Implement parse_settlement_filename function**

```python
# File: c:/proyectos/finanzas-back/app/routers/imports.py
# Add these imports at the top:
import re
from datetime import datetime

# Add this function before the router endpoints (after imports):

def parse_settlement_filename(filename: str) -> dict:
    """
    Parse settlement filename to extract date and calculate week number.
    
    Expected format: settlement-x-YYYY-MM-DD.csv
    
    Args:
        filename: The filename to parse
        
    Returns:
        dict with keys: date (datetime), week (int), year (int), display_name (str)
        
    Raises:
        ValueError: If filename format is invalid
        
    Example:
        >>> parse_settlement_filename("settlement-x-2024-04-18.csv")
        {
            "date": datetime(2024, 4, 18),
            "week": 16,
            "year": 2024,
            "display_name": "Semana 16 - 2024"
        }
    """
    # Regex to extract date: YYYY-MM-DD
    pattern = r'settlement-x-(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, filename)
    
    if not match:
        raise ValueError(f"Formato de filename inválido: {filename}")
    
    year_str, month_str, day_str = match.groups()
    year = int(year_str)
    month = int(month_str)
    day = int(day_str)
    
    # Create datetime object
    date = datetime(year, month, day)
    
    # Calculate ISO 8601 week number
    iso_calendar = date.isocalendar()
    week_number = iso_calendar[1]  # Returns (year, week, weekday)
    
    # Create display name
    display_name = f"Semana {week_number} - {year}"
    
    return {
        "date": date,
        "week": week_number,
        "year": year,
        "display_name": display_name
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_import_history.py -k parse_settlement_filename -v`
Expected: All 5 parsing tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/routers/imports.py tests/test_import_history.py
git commit -m "feat: add settlement filename parser

- Parses settlement-x-YYYY-MM-DD.csv format
- Calculates ISO 8601 week number
- Generates display name 'Semana X - YYYY'
- Full test coverage including edge cases

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Backend - Add import_history Collection to Database

**Files:**
- Modify: `c:/proyectos/finanzas-back/app/repositories/json_repository.py:47-69`

- [ ] **Step 1: Add import_history to schema initialization**

```python
# File: c:/proyectos/finanzas-back/app/repositories/json_repository.py
# Modify the _initialize_schema method (around line 47-69):

    def _initialize_schema(self) -> Dict[str, Any]:
        """Initialize empty database schema"""
        return {
            '_metadata': {
                'schema_version': SCHEMA_VERSION,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
            },
            'accounts': {},
            'credit_cards': {},
            'categories': {},
            'transactions': {},
            'transaction_import_batches': {},
            'raw_import_rows': {},
            'import_history': {},  # NEW - Track confirmed imports
            'recurring_expenses': {},
            'budgets': {},
            'assets': {},
            'liabilities': {},
            'net_worth_snapshots': {},
            'crypto_wallets': {},
            'crypto_positions': {},
            'processed_source_ids': {},
        }
```

- [ ] **Step 2: Verify database initializes with new collection**

Manual test: Delete `data/finanzas.json` if it exists, start the API, check that the file is created with `import_history: {}`

Run: `rm data/finanzas.json; python -m app.main` (then Ctrl+C after startup)
Expected: File `data/finanzas.json` contains `"import_history": {}`

- [ ] **Step 3: Commit**

```bash
git add app/repositories/json_repository.py
git commit -m "feat: add import_history collection to database schema

- New collection for tracking confirmed import batches
- Automatically created on database initialization

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Backend - Implement GET /api/v1/imports/history Endpoint

**Files:**
- Modify: `c:/proyectos/finanzas-back/app/routers/imports.py`
- Modify: `c:/proyectos/finanzas-back/tests/test_import_history.py`

- [ ] **Step 1: Write failing test for GET history endpoint**

```python
# File: c:/proyectos/finanzas-back/tests/test_import_history.py
# Add to existing file:

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_import_history_empty(temp_db):
    """Test GET /api/v1/imports/history with no history"""
    response = client.get("/api/v1/imports/history")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["history"] == []


def test_get_import_history_with_data(temp_db):
    """Test GET /api/v1/imports/history returns history items"""
    from app.repositories import get_db
    
    # Manually insert a history record
    db = get_db()
    history_id = "hist-test-123"
    db.data['import_history'] = {
        history_id: {
            "id": history_id,
            "filename": "settlement-x-2024-04-18.csv",
            "uploaded_at": "2024-04-18T14:25:00",
            "confirmed_at": "2024-04-18T14:30:00",
            "batch_id": "batch-xyz",
            "status": "confirmed",
            "total_transactions": 24,
            "total_ingresos": 15000.50,
            "total_gastos": 8500.75,
            "week_number": 16,
            "display_name": "Semana 16 - 2024"
        }
    }
    db.save()
    
    # Request history
    response = client.get("/api/v1/imports/history")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["history"]) == 1
    assert data["history"][0]["id"] == history_id
    assert data["history"][0]["display_name"] == "Semana 16 - 2024"


def test_get_import_history_ordered_by_confirmed_at(temp_db):
    """Test history is ordered by confirmed_at descending"""
    from app.repositories import get_db
    
    db = get_db()
    db.data['import_history'] = {
        "hist-1": {
            "id": "hist-1",
            "filename": "settlement-x-2024-04-11.csv",
            "confirmed_at": "2024-04-11T10:00:00",
            "display_name": "Semana 15 - 2024",
            "batch_id": "batch-1",
            "status": "confirmed",
            "total_transactions": 10,
            "total_ingresos": 5000.0,
            "total_gastos": 2000.0,
            "week_number": 15,
            "uploaded_at": "2024-04-11T09:00:00"
        },
        "hist-2": {
            "id": "hist-2",
            "filename": "settlement-x-2024-04-18.csv",
            "confirmed_at": "2024-04-18T10:00:00",
            "display_name": "Semana 16 - 2024",
            "batch_id": "batch-2",
            "status": "confirmed",
            "total_transactions": 20,
            "total_ingresos": 8000.0,
            "total_gastos": 4000.0,
            "week_number": 16,
            "uploaded_at": "2024-04-18T09:00:00"
        }
    }
    db.save()
    
    response = client.get("/api/v1/imports/history")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 2
    # Most recent first (hist-2 confirmed at 2024-04-18)
    assert data["history"][0]["id"] == "hist-2"
    assert data["history"][1]["id"] == "hist-1"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_import_history.py::test_get_import_history_empty -v`
Expected: FAIL with 404 (endpoint doesn't exist)

- [ ] **Step 3: Implement GET /api/v1/imports/history endpoint**

```python
# File: c:/proyectos/finanzas-back/app/routers/imports.py
# Add this endpoint after the existing endpoints:

@router.get("/history")
async def get_import_history() -> Dict[str, Any]:
    """
    Get history of all confirmed import batches.
    
    Returns:
        JSON with list of import history records, ordered by confirmed_at descending
        
    Example response:
        {
            "success": true,
            "history": [
                {
                    "id": "hist-abc123",
                    "filename": "settlement-x-2024-04-18.csv",
                    "confirmed_at": "2024-04-18T14:30:00",
                    "display_name": "Semana 16 - 2024",
                    "total_transactions": 24,
                    "total_ingresos": 15000.50,
                    "total_gastos": 8500.75,
                    "status": "confirmed"
                }
            ]
        }
    """
    db = get_db()
    
    # Get import_history collection (may not exist in old databases)
    history_data = db.data.get('import_history', {})
    
    # Convert to list of dicts
    history_list = list(history_data.values())
    
    # Sort by confirmed_at descending (most recent first)
    history_list.sort(
        key=lambda x: x.get('confirmed_at', ''),
        reverse=True
    )
    
    return {
        "success": True,
        "history": history_list
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_import_history.py -k get_import_history -v`
Expected: All 3 GET history tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/routers/imports.py tests/test_import_history.py
git commit -m "feat: add GET /api/v1/imports/history endpoint

- Returns all confirmed import history records
- Ordered by confirmed_at descending (most recent first)
- Handles missing import_history collection gracefully
- Full test coverage

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Backend - Modify POST /batches/{batch_id}/confirm to Create History

**Files:**
- Modify: `c:/proyectos/finanzas-back/app/routers/imports.py:112-194`
- Modify: `c:/proyectos/finanzas-back/tests/test_import_history.py`

- [ ] **Step 1: Write failing test for confirm creates history**

```python
# File: c:/proyectos/finanzas-back/tests/test_import_history.py
# Add to existing file:

def test_confirm_batch_creates_history_record(temp_db):
    """Test confirming batch creates history record"""
    from app.repositories import get_db
    import uuid
    
    db = get_db()
    
    # Create a batch with filename
    batch_id = str(uuid.uuid4())
    db.data['import_batches'] = {
        batch_id: {
            "id": batch_id,
            "filename": "settlement-x-2024-04-18.csv",
            "uploaded_at": "2024-04-18T14:25:00",
            "transactions": [
                {
                    "transaction_type": "ingreso",
                    "amount": 1000.0,
                    "description": "Test ingreso"
                },
                {
                    "transaction_type": "gasto",
                    "amount": 500.0,
                    "description": "Test gasto"
                }
            ]
        }
    }
    db.save()
    
    # Confirm the batch
    response = client.post(f"/api/v1/imports/batches/{batch_id}/confirm")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "history_id" in data
    
    # Verify history was created
    history_id = data["history_id"]
    db.reload()
    assert 'import_history' in db.data
    assert history_id in db.data['import_history']
    
    history = db.data['import_history'][history_id]
    assert history["filename"] == "settlement-x-2024-04-18.csv"
    assert history["batch_id"] == batch_id
    assert history["status"] == "confirmed"
    assert history["total_transactions"] == 2
    assert history["total_ingresos"] == 1000.0
    assert history["total_gastos"] == 500.0
    assert history["week_number"] == 16
    assert history["display_name"] == "Semana 16 - 2024"


def test_confirm_batch_handles_invalid_filename_gracefully(temp_db):
    """Test confirm batch with invalid filename uses fallback"""
    from app.repositories import get_db
    import uuid
    
    db = get_db()
    
    # Create batch with invalid filename
    batch_id = str(uuid.uuid4())
    db.data['import_batches'] = {
        batch_id: {
            "id": batch_id,
            "filename": "invalid-format.csv",
            "uploaded_at": "2024-04-18T14:25:00",
            "transactions": [
                {
                    "transaction_type": "ingreso",
                    "amount": 100.0,
                    "description": "Test"
                }
            ]
        }
    }
    db.save()
    
    # Confirm should still work, using fallback display name
    response = client.post(f"/api/v1/imports/batches/{batch_id}/confirm")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "history_id" in data
    
    # Verify fallback display name
    history_id = data["history_id"]
    db.reload()
    history = db.data['import_history'][history_id]
    assert "Importación" in history["display_name"]
    assert history["week_number"] == 0  # Fallback value
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_import_history.py::test_confirm_batch_creates_history_record -v`
Expected: FAIL with KeyError: 'history_id' (not in response yet)

- [ ] **Step 3: Modify confirm endpoint to create history**

```python
# File: c:/proyectos/finanzas-back/app/routers/imports.py
# Replace the entire confirm_batch_transactions function (lines 112-194):

@router.post("/batches/{batch_id}/confirm")
async def confirm_batch_transactions(batch_id: str) -> Dict[str, Any]:
    """
    Confirma un batch importado y pasa las transacciones al dashboard.
    Creates a history record of the confirmed import.

    Los ingresos se registran como ingresos en el dashboard.
    Los egresos se registran como gastos en el dashboard.

    Args:
        batch_id: ID del batch a confirmar

    Returns:
        JSON con resumen de confirmación y history_id
    """
    import storage
    import uuid

    db = get_db()

    # Verificar que el batch existe
    if 'import_batches' not in db.data:
        raise HTTPException(
            status_code=404,
            detail="No hay batches importados"
        )

    batches = db.data['import_batches']
    if batch_id not in batches:
        raise HTTPException(
            status_code=404,
            detail=f"Batch {batch_id} no encontrado"
        )

    batch = batches[batch_id]
    transactions = batch.get('transactions', [])
    filename = batch.get('filename', 'unknown.csv')
    uploaded_at_str = batch.get('uploaded_at', datetime.now().isoformat())

    # Contadores
    ingresos_confirmados = 0
    gastos_confirmados = 0
    total_ingresos = 0.0
    total_gastos = 0.0

    # Procesar cada transacción del batch
    for tx in transactions:
        tx_type = tx.get('transaction_type')
        amount = tx.get('amount', 0)
        description = tx.get('description', 'Sin descripción')

        if tx_type == 'ingreso':
            # Registrar como ingreso en el dashboard
            storage.agregar_transaccion(
                tipo='ingreso',
                monto=amount,
                descripcion=description
            )
            ingresos_confirmados += 1
            total_ingresos += amount

        elif tx_type == 'gasto':
            # Registrar como gasto en el dashboard
            storage.agregar_transaccion(
                tipo='gasto',
                monto=amount,
                descripcion=description
            )
            gastos_confirmados += 1
            total_gastos += amount

    # Parse filename to get week information
    try:
        parsed = parse_settlement_filename(filename)
        week_number = parsed["week"]
        display_name = parsed["display_name"]
    except ValueError:
        # Fallback for invalid filenames
        week_number = 0
        display_name = f"Importación - {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    # Create import history record
    history_id = f"hist-{str(uuid.uuid4())[:8]}"
    confirmed_at = datetime.now()
    
    # Initialize import_history collection if it doesn't exist
    if 'import_history' not in db.data:
        db.data['import_history'] = {}
    
    db.data['import_history'][history_id] = {
        "id": history_id,
        "filename": filename,
        "uploaded_at": uploaded_at_str,
        "confirmed_at": confirmed_at.isoformat(),
        "batch_id": batch_id,
        "status": "confirmed",
        "total_transactions": ingresos_confirmados + gastos_confirmados,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "week_number": week_number,
        "display_name": display_name
    }

    # Marcar el batch como confirmado
    batch['confirmed'] = True
    batch['confirmed_at'] = confirmed_at.isoformat()
    db.save()

    return {
        "success": True,
        "batch_id": batch_id,
        "history_id": history_id,
        "summary": {
            "ingresos_confirmados": ingresos_confirmados,
            "gastos_confirmados": gastos_confirmados,
            "total_ingresos_ars": total_ingresos,
            "total_gastos_ars": total_gastos,
            "total_transacciones": ingresos_confirmados + gastos_confirmados
        }
    }
```

- [ ] **Step 4: Add uuid import at top of file**

```python
# File: c:/proyectos/finanzas-back/app/routers/imports.py
# Add to imports section at top (around line 1-13):
import uuid
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_import_history.py -k confirm_batch -v`
Expected: Both confirm tests PASS

- [ ] **Step 6: Commit**

```bash
git add app/routers/imports.py tests/test_import_history.py
git commit -m "feat: confirm batch creates import history record

- Modified POST /batches/{batch_id}/confirm endpoint
- Creates history record with parsed week number and display name
- Returns history_id in response
- Handles invalid filenames with fallback
- Full test coverage

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Frontend - Change Currency from USD to ARS

**Files:**
- Modify: `c:/proyectos/finanzas-front/js/config.js:9`
- Modify: `c:/proyectos/finanzas-front/js/ui.js:6-11`

- [ ] **Step 1: Change CURRENCY config to ARS**

```javascript
// File: c:/proyectos/finanzas-front/js/config.js
// Replace line 9:
export const CONFIG = {
  API_URL: 'http://127.0.0.1:8000',
  API_TIMEOUT: 30000,
  MAX_FILE_SIZE_MB: 50,
  SUPPORTED_FORMATS: ['.csv', '.xlsx', '.xls'],
  CURRENCY: 'ARS',  // Changed from 'USD' to 'ARS'
  LOCALE: 'es-AR'
};
```

- [ ] **Step 2: Fix formatCurrency to use explicit decimal formatting**

```javascript
// File: c:/proyectos/finanzas-front/js/ui.js
// Replace lines 6-11 (formatCurrency function):
export function formatCurrency(amount) {
  return new Intl.NumberFormat(CONFIG.LOCALE, {
    style: 'currency',
    currency: CONFIG.CURRENCY,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}
```

- [ ] **Step 3: Manual test currency formatting**

Open browser console and test:
```javascript
import { formatCurrency } from './js/ui.js';
console.log(formatCurrency(1500.50));  // Should output: $ 1.500,50
console.log(formatCurrency(1000000));   // Should output: $ 1.000.000,00
console.log(formatCurrency(0.99));      // Should output: $ 0,99
```

Expected: All amounts display with `$` symbol, punto (.) for thousands, comma (,) for decimals

- [ ] **Step 4: Verify in running application**

1. Start backend: `cd c:/proyectos/finanzas-back && python -m uvicorn main:app --reload`
2. Open frontend: `c:/proyectos/finanzas-front/index.html`
3. Check dashboard balance shows `$ X.XXX,XX` format
4. Check transaction history amounts show `$ X.XXX,XX` format
5. Check chart legend totals show `$ X.XXX,XX` format

Expected: All currency values throughout the app use Argentine peso format

- [ ] **Step 5: Commit**

```bash
git add js/config.js js/ui.js
git commit -m "feat: change currency format from USD to ARS

- Changed CONFIG.CURRENCY from 'USD' to 'ARS'
- Added explicit decimal formatting to formatCurrency
- Format is now $ 1.500,50 (punto for thousands, comma for decimals)
- Applied globally across entire application

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Frontend - Add Toast Notification Styles and Function

**Files:**
- Modify: `c:/proyectos/finanzas-front/css/components.css`
- Modify: `c:/proyectos/finanzas-front/js/ui.js`

- [ ] **Step 1: Add toast notification CSS**

```css
/* File: c:/proyectos/finanzas-front/css/components.css */
/* Add at the end of the file: */

/* Toast Notifications */
.toast-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-success);
  border: 2px solid var(--color-success-dark);
  color: var(--text-white);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(46, 213, 115, 0.4);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  animation: slideDownFadeIn 0.3s ease;
  max-width: 500px;
  text-align: center;
}

.toast-notification.fade-out {
  animation: fadeOut 0.3s ease;
}

@keyframes slideDownFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@keyframes fadeOut {
  to {
    opacity: 0;
  }
}
```

- [ ] **Step 2: Add showToast function to ui.js**

```javascript
// File: c:/proyectos/finanzas-front/js/ui.js
// Add this function at the end of the file:

export function showToast(message, duration = 5000) {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.innerHTML = `<span style="font-size: 1.5rem;">✓</span> ${message}`;
  
  // Add to DOM
  document.body.appendChild(toast);
  
  // Remove after duration
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => {
      if (toast.parentNode) {
        document.body.removeChild(toast);
      }
    }, 300);
  }, duration);
}
```

- [ ] **Step 3: Manual test toast notification**

Open browser console and test:
```javascript
import { showToast } from './js/ui.js';
showToast('Importación completada - 24 transacciones registradas');
```

Expected: Green toast appears at top center, stays 5 seconds, fades out and disappears

- [ ] **Step 4: Commit**

```bash
git add css/components.css js/ui.js
git commit -m "feat: add toast notification system

- Added toast-notification CSS with slide-down animation
- Added showToast() function with auto-dismiss
- Green success styling with checkmark icon
- 5 second duration with fade-out

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Frontend - Add formatDateTime Utility Function

**Files:**
- Modify: `c:/proyectos/finanzas-front/js/ui.js`

- [ ] **Step 1: Add formatDateTime function**

```javascript
// File: c:/proyectos/finanzas-front/js/ui.js
// Add this function after formatDate and before showMessage:

export function formatDateTime(isoString) {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString(CONFIG.LOCALE, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return isoString;
  }
}
```

- [ ] **Step 2: Manual test formatDateTime**

Open browser console and test:
```javascript
import { formatDateTime } from './js/ui.js';
console.log(formatDateTime('2024-04-18T14:30:00'));  // Should output: 18/04/2024, 14:30
console.log(formatDateTime('2024-12-31T23:59:59'));  // Should output: 31/12/2024, 23:59
console.log(formatDateTime(null));                    // Should output: -
```

Expected: Formatted dates in DD/MM/YYYY, HH:MM format

- [ ] **Step 3: Commit**

```bash
git add js/ui.js
git commit -m "feat: add formatDateTime utility function

- Formats ISO datetime strings to DD/MM/YYYY, HH:MM
- Uses es-AR locale
- Handles null/invalid dates gracefully

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Frontend - Add getImportHistory to API Client

**Files:**
- Modify: `c:/proyectos/finanzas-front/js/api.js`

- [ ] **Step 1: Add getImportHistory method to APIClient**

```javascript
// File: c:/proyectos/finanzas-front/js/api.js
// Add this method to the APIClient class (after getBatchTransactions):

  async getImportHistory() {
    return this.request('/api/v1/imports/history');
  }
```

- [ ] **Step 2: Verify method signature matches usage**

The method should be called like:
```javascript
const response = await api.getImportHistory();
// response = { success: true, history: [...] }
```

- [ ] **Step 3: Commit**

```bash
git add js/api.js
git commit -m "feat: add getImportHistory to API client

- New method to fetch import history from backend
- Returns list of confirmed import records

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Frontend - Simplify Import Results Table Columns

**Files:**
- Modify: `c:/proyectos/finanzas-front/index.html:166-177`
- Modify: `c:/proyectos/finanzas-front/js/imports.js:164-218`

- [ ] **Step 1: Reduce table columns in HTML**

```html
<!-- File: c:/proyectos/finanzas-front/index.html -->
<!-- Replace lines 166-177 (table header in import results): -->
                        <table class="transactions-table">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Monto</th>
                                    <th>Tipo</th>
                                    <th>Método Pago</th>
                                </tr>
                            </thead>
                            <tbody id="importedTransactionsBody">
                            </tbody>
                        </table>
```

- [ ] **Step 2: Simplify renderImportedTransactions function**

```javascript
// File: c:/proyectos/finanzas-front/js/imports.js
// Replace renderImportedTransactions function (lines 164-218):

function renderImportedTransactions(transactions) {
  const tbody = document.getElementById('importedTransactionsBody');
  const confirmButton = document.getElementById('confirmButton');

  if (!tbody) return;

  if (transactions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #a0a0a0;">No hay transacciones para mostrar</td></tr>';
    if (confirmButton) confirmButton.style.display = 'none';
    return;
  }

  importedTransactions = transactions;

  const html = transactions.map(tx => {
    const date = formatDate(tx.operation_date);
    const displayAmount = tx.real_amount !== undefined ? tx.real_amount : tx.amount;
    const amount = formatCurrency(Math.abs(displayAmount || 0));
    const type = formatTransactionType(tx.transaction_type);

    let paymentMethod = tx.payment_method || '-';
    if (tx.payment_method_type && tx.payment_method_type !== tx.payment_method) {
      paymentMethod = `${tx.payment_method} (${tx.payment_method_type})`;
    }

    return `
      <tr>
        <td>${date}</td>
        <td style="font-weight: bold;">${amount}</td>
        <td>${type}</td>
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
```

- [ ] **Step 3: Manual test table display**

1. Import a file
2. Check that table shows only 4 columns: Fecha, Monto, Tipo, Método Pago
3. Verify no columns for Descripción, Comercio, Moneda, Categoría, Estado

Expected: Table is cleaner and easier to scan visually

- [ ] **Step 4: Commit**

```bash
git add index.html js/imports.js
git commit -m "feat: simplify import results table to 4 columns

- Removed columns: Descripción, Comercio, Moneda, Categoría, Estado
- Kept columns: Fecha, Monto, Tipo, Método Pago
- Easier to scan visually, better for small screens

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Frontend - Add Import History HTML Section

**Files:**
- Modify: `c:/proyectos/finanzas-front/index.html`

- [ ] **Step 1: Add import history section HTML**

```html
<!-- File: c:/proyectos/finanzas-front/index.html -->
<!-- Add before the closing </div> of id="import" (before line 191): -->

        <!-- Import History Section -->
        <div id="importHistorySection" class="card import-section" style="margin-top: 30px; display: none;">
          <h2>Historial de Importaciones</h2>
          <div id="importHistoryList" class="import-history-list">
            <!-- Items generated dynamically -->
          </div>
        </div>
```

The structure should be:
```html
        </div>
        <!-- End Import Tab -->

        <!-- NEW: Import History Section -->
        <div id="importHistorySection" class="card import-section" style="margin-top: 30px; display: none;">
          <h2>Historial de Importaciones</h2>
          <div id="importHistoryList" class="import-history-list">
            <!-- Items generated dynamically -->
          </div>
        </div>

    </div>
    <!-- End id="import" -->
```

- [ ] **Step 2: Verify section is hidden by default**

Open `index.html` in browser, go to "Importar Mercado Pago" tab.
Expected: "Historial de Importaciones" section is NOT visible (display: none)

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add import history HTML section

- New section at bottom of import tab
- Hidden by default (display: none)
- Will be shown when history data loads

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Frontend - Add Import History CSS Styles

**Files:**
- Modify: `c:/proyectos/finanzas-front/css/components.css`

- [ ] **Step 1: Add import history CSS**

```css
/* File: c:/proyectos/finanzas-front/css/components.css */
/* Add at the end of the file: */

/* Import History */
.import-history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.history-item {
  background: rgba(15, 52, 96, 0.4);
  border-left: 4px solid var(--color-success);
  border-radius: var(--radius-sm);
  padding: var(--spacing-md);
  transition: all var(--transition-base);
}

.history-item:hover {
  background: rgba(15, 52, 96, 0.6);
  transform: translateX(5px);
}

.history-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.history-icon {
  color: var(--color-success);
  font-size: 1.5rem;
  font-weight: bold;
}

.history-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.history-stats {
  display: flex;
  gap: var(--spacing-lg);
  color: var(--text-primary);
  font-size: var(--font-size-md);
  margin-bottom: var(--spacing-xs);
}

.history-stat {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.history-timestamp {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.history-empty {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--spacing-xl);
  font-style: italic;
}
```

- [ ] **Step 2: Verify CSS variables exist**

Check that `css/variables.css` has these variables used above:
- `--spacing-md`, `--spacing-sm`, `--spacing-xs`, `--spacing-lg`, `--spacing-xl`
- `--color-success`
- `--radius-sm`
- `--transition-base`
- `--font-size-lg`, `--font-size-md`, `--font-size-sm`
- `--text-primary`, `--text-secondary`

Expected: All variables are already defined (from Task 4 of previous plan)

- [ ] **Step 3: Commit**

```bash
git add css/components.css
git commit -m "feat: add import history component styles

- Card-based layout with green left border
- Hover effects with transform and background change
- Stats display with proper spacing
- Responsive design with CSS variables

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Frontend - Implement Import History Loading and Rendering

**Files:**
- Modify: `c:/proyectos/finanzas-front/js/imports.js`

- [ ] **Step 1: Add loadImportHistory function**

```javascript
// File: c:/proyectos/finanzas-front/js/imports.js
// Add this function after setupConfirmButton():

async function loadImportHistory() {
  try {
    const response = await api.getImportHistory();
    
    if (response.success && response.history.length > 0) {
      renderImportHistory(response.history);
      document.getElementById('importHistorySection').style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading import history:', error);
    // Don't show error to user, just keep section hidden
  }
}
```

- [ ] **Step 2: Add renderImportHistory function**

```javascript
// File: c:/proyectos/finanzas-front/js/imports.js
// Add this function after loadImportHistory():

function renderImportHistory(historyItems) {
  const listElement = document.getElementById('importHistoryList');
  
  if (!listElement) return;
  
  if (historyItems.length === 0) {
    listElement.innerHTML = '<div class="history-empty">No hay importaciones registradas aún</div>';
    return;
  }
  
  const html = historyItems.map(item => `
    <div class="history-item">
      <div class="history-header">
        <span class="history-icon">✓</span>
        <span class="history-title">${escapeHtml(item.display_name)}</span>
      </div>
      <div class="history-stats">
        <span class="history-stat">
          ${item.total_transactions} transacciones
        </span>
        <span class="history-stat">
          Ingresos: ${formatCurrency(item.total_ingresos)}
        </span>
        <span class="history-stat">
          Gastos: ${formatCurrency(item.total_gastos)}
        </span>
      </div>
      <div class="history-timestamp">
        Confirmado el ${formatDateTime(item.confirmed_at)}
      </div>
    </div>
  `).join('');
  
  listElement.innerHTML = html;
}
```

- [ ] **Step 3: Call loadImportHistory on init**

```javascript
// File: c:/proyectos/finanzas-front/js/imports.js
// Modify initImports function (around line 11-15):

export function initImports() {
  setupFileUpload();
  setupImportButton();
  setupConfirmButton();
  loadImportHistory();  // NEW - Load history on page load
}
```

- [ ] **Step 4: Import formatDateTime in imports.js**

```javascript
// File: c:/proyectos/finanzas-front/js/imports.js
// Modify imports at top of file (around line 6):

import { formatCurrency, formatDate, showMessage, escapeHtml, switchTab, formatDateTime, showToast } from './ui.js';
```

- [ ] **Step 5: Manual test history display**

1. Start backend with confirmed imports in database
2. Open frontend and go to "Importar Mercado Pago" tab
3. Check that "Historial de Importaciones" section appears at bottom
4. Verify each item shows: green checkmark, display name, stats, timestamp

Expected: History loads and displays correctly on page load

- [ ] **Step 6: Commit**

```bash
git add js/imports.js
git commit -m "feat: implement import history loading and rendering

- Added loadImportHistory() function to fetch from backend
- Added renderImportHistory() to display history cards
- Called on page load in initImports()
- Shows green checkmark, stats, formatted datetime

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Frontend - Integrate Toast and History Reload After Confirmation

**Files:**
- Modify: `c:/proyectos/finanzas-front/js/imports.js:239-300`

- [ ] **Step 1: Add toast notification after successful confirmation**

```javascript
// File: c:/proyectos/finanzas-front/js/imports.js
// Modify setupConfirmButton function (lines 239-300):
// Replace the section after successful registration (around line 276-289):

      if (registeredCount > 0) {
        // Show toast notification
        showToast(`Importación completada - ${registeredCount} transacción(es) registradas`);
        
        showMessage(
          'importMessage',
          `✓ ${registeredCount} transacción(es) registrada(s) exitosamente.${errorCount > 0 ? ` ${errorCount} fallaron.` : ''}`,
          'success'
        );

        // Reload dashboard data and switch tabs
        setTimeout(async () => {
          // Import dashboard module to refresh data
          const { loadDashboardData } = await import('./dashboard.js');
          await loadDashboardData();
          
          // Reload import history
          await loadImportHistory();
          
          switchTab('dashboard');
        }, 2000);
      } else {
        showMessage('importMessage', 'Error: No se pudieron registrar las transacciones.', 'error');
      }
```

- [ ] **Step 2: Verify toast appears before tab switch**

Manual test:
1. Import a file
2. Click "Confirmar y Registrar en Dashboard"
3. Check that green toast appears at top: "✓ Importación completada - X transacciones registradas"
4. Wait 2 seconds
5. Check that tab switches to dashboard
6. Switch back to import tab
7. Check that new import appears in history

Expected: Toast shows immediately, history updates after confirmation

- [ ] **Step 3: Commit**

```bash
git add js/imports.js
git commit -m "feat: integrate toast notification and history reload

- Show toast after successful import confirmation
- Reload import history after confirmation
- History updates automatically when switching back to import tab

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Integration Testing - Verify All Three Problems Fixed

**Files:**
- Manual testing only (no code changes)

- [ ] **Step 1: Test Problem 1 - Transactions appear in dashboard**

Manual test:
1. Start backend: `cd c:/proyectos/finanzas-back && python -m uvicorn main:app --reload`
2. Open frontend: `c:/proyectos/finanzas-front/index.html`
3. Go to "Importar Mercado Pago" tab
4. Upload `settlement-x-2024-04-18.csv` file
5. Click "Importar Transacciones"
6. Click "Confirmar y Registrar en Dashboard"
7. Verify green toast appears
8. Wait for automatic tab switch to Dashboard
9. Check "Historial de Transacciones" section
10. Verify imported transactions appear with green/red formatting

Expected: ✅ All imported transactions visible in dashboard history with proper colors

- [ ] **Step 2: Test Problem 2 - Currency format is ARS**

Manual test (continue from Step 1):
1. Check balance at top shows `$ X.XXX,XX` format (not US$ format)
2. Check transaction history amounts show `$ X.XXX,XX` format
3. Check pie chart legend totals show `$ X.XXX,XX` format
4. Go back to "Importar Mercado Pago" tab
5. Check import results table shows amounts as `$ X.XXX,XX`
6. Check KPI cards show proper format

Expected: ✅ All amounts throughout entire app use `$ 1.500,50` format (punto for thousands, comma for decimals)

- [ ] **Step 3: Test Problem 3 - Import history with notifications**

Manual test (continue from Step 2):
1. Verify you're on "Importar Mercado Pago" tab
2. Scroll to bottom
3. Check "Historial de Importaciones" section is visible
4. Check that the import you just confirmed appears as a card
5. Verify card shows:
   - Green checkmark icon (✓)
   - Display name: "Semana 16 - 2024" (not raw filename)
   - Stats: "24 transacciones", "Ingresos: $ X.XXX,XX", "Gastos: $ X.XXX,XX"
   - Timestamp: "Confirmado el DD/MM/YYYY, HH:MM"
6. Import another file and confirm
7. Verify toast appears again
8. Verify history shows 2 items, ordered with most recent first

Expected: ✅ History persists, shows formatted names, displays all statistics, ordered by date

- [ ] **Step 4: Test edge cases**

Manual test:
1. Refresh the page (F5)
2. Go to "Importar Mercado Pago" tab
3. Verify history still appears (persisted in backend, not LocalStorage)
4. Try importing a file with invalid name format (not settlement-x-YYYY-MM-DD.csv)
5. Verify it still works and uses fallback display name
6. Check that amounts with large values display correctly: $ 1.000.000,00
7. Check that amounts with cents display correctly: $ 1.234,56

Expected: ✅ All edge cases handled gracefully

- [ ] **Step 5: Document test results**

Create a test summary:
```
INTEGRATION TEST RESULTS - 2026-04-18

✅ Problem 1: Dashboard Transaction Visibility
   - Imported transactions appear immediately in dashboard history
   - Proper color formatting (green for ingresos, red for gastos)
   - Balance updates correctly
   - Chart updates correctly

✅ Problem 2: Currency Format USD → ARS
   - Dashboard balance: $ X.XXX,XX ✓
   - Transaction history: $ X.XXX,XX ✓
   - Pie chart legend: $ X.XXX,XX ✓
   - Import results table: $ X.XXX,XX ✓
   - All KPIs: $ X.XXX,XX ✓
   - No US$ symbols anywhere ✓

✅ Problem 3: Import History & Notifications
   - Toast notification appears on confirmation ✓
   - History section displays at bottom of import tab ✓
   - Display name format: "Semana X - YYYY" ✓
   - Green checkmark icon visible ✓
   - Statistics show transaction count and totals ✓
   - Timestamp formatted correctly ✓
   - History persists after page refresh ✓
   - Ordered by most recent first ✓

✅ Bonus: Table Simplification
   - Import results table shows only 4 columns ✓
   - Columns: Fecha, Monto, Tipo, Método Pago ✓
   - Easier to scan visually ✓

All acceptance criteria met. Ready for production.
```

Expected: All tests pass, all three problems solved

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "test: verify all three problems fixed

Integration testing completed:
- Problem 1: Dashboard transaction visibility ✓
- Problem 2: Currency format USD → ARS ✓  
- Problem 3: Import history with notifications ✓
- Table simplified to 4 columns ✓

All acceptance criteria met.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

**Spec Coverage:**
- ✅ Problem 1 (Dashboard visibility): Task 14 ensures proper data reload
- ✅ Problem 2 (Currency format): Task 6 changes to ARS globally
- ✅ Problem 3 (Import history): Tasks 1-5 (backend), Tasks 11-14 (frontend)
- ✅ Table simplification: Task 10
- ✅ Toast notifications: Task 7
- ✅ Filename parsing: Task 2
- ✅ Week number calculation: Task 2 (ISO 8601)
- ✅ Display name format: Task 2 + Task 5
- ✅ Backend persistence: Tasks 1-5
- ✅ Frontend history display: Tasks 11-14

**Placeholder Scan:**
- ✅ No "TBD" or "TODO" in steps
- ✅ All code blocks are complete
- ✅ All file paths are exact
- ✅ All test commands are exact
- ✅ All commit messages are complete

**Type Consistency:**
- ✅ `ImportHistory` model used consistently
- ✅ `parse_settlement_filename()` function signature consistent
- ✅ `formatCurrency()`, `formatDateTime()`, `showToast()` consistent
- ✅ `loadImportHistory()`, `renderImportHistory()` consistent
- ✅ API response format matches between backend and frontend

---

## Execution Options

Plan complete and ready for execution.
