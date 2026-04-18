"""
Integration tests for import endpoints
"""
import io
import pytest
from fastapi.testclient import TestClient


def _upload_csv(client: TestClient, csv_content: str, filename: str = "test.csv"):
    """Helper function to upload CSV file"""
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    return client.post(
        "/api/v1/imports/upload",
        files={"file": (filename, csv_file, "text/csv")},
        data={"source_type": "mercadopago_csv"}
    )


def test_upload_csv_import(client: TestClient, sample_csv_content: str):
    """Test uploading a CSV file for import"""
    response = _upload_csv(client, sample_csv_content)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "batch" in data
    assert data["batch"]["total_rows"] == 2  # sample_csv_content has exactly 2 data rows
    assert data["batch"]["processed_rows"] > 0
    assert "id" in data["batch"]
    assert len(data["batch"]["id"]) > 0


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
    upload_response = _upload_csv(client, sample_csv_content)

    assert upload_response.status_code == 200
    batch_id = upload_response.json()["batch"]["id"]

    # Retrieve batch transactions
    get_response = client.get(f"/api/v1/imports/batches/{batch_id}/transactions")

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["success"] is True
    assert data["batch_id"] == batch_id
    assert "transactions" in data
