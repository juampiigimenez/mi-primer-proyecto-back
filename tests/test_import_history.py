import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.models.import_history import ImportHistory
from app.routers.imports import parse_settlement_filename
from app.main import app

client = TestClient(app)

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
