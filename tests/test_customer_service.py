import pytest
from fastapi.testclient import TestClient
from customer_service import app

client = TestClient(app)

def test_create_customer():
    response = client.post(
        "/customers/",
        json={
            "full_name": "Test User",
            "username": "testuser",
            "password": "password123",
            "age": 25,
            "address": "Test Address",
            "gender": "male",
            "marital_status": "single"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"