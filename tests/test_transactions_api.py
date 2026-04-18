"""
Integration tests for transaction CRUD endpoints
"""
import pytest
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


def test_update_transaction_not_found(client: TestClient):
    """Test updating non-existent transaction"""
    updated_data = {
        "monto": 2000.0,
        "tipo": "gasto",
        "descripcion": "Updated"
    }
    response = client.put("/api/v1/transactions/99999", json=updated_data)
    assert response.status_code == 404


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
