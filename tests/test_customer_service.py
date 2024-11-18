import pytest
from fastapi.testclient import TestClient
from customer_service import app, Customer
from decimal import Decimal

client = TestClient(app)

@pytest.fixture
def sample_customer_data():
    return {
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepass123",
        "age": 30,
        "address": "123 Test St",
        "gender": "male",
        "marital_status": "single"
    }

def test_create_customer(test_db, sample_customer_data):
    response = client.post("/customers/", json=sample_customer_data)
    assert response.status_code == 200
    assert response.json()["username"] == sample_customer_data["username"]
    assert response.json()["full_name"] == sample_customer_data["full_name"]

def test_create_duplicate_customer(test_db, sample_customer_data):
    # Create first customer
    client.post("/customers/", json=sample_customer_data)
    # Try to create duplicate
    response = client.post("/customers/", json=sample_customer_data)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_get_customer(test_db, sample_customer_data):
    # Create customer first
    client.post("/customers/", json=sample_customer_data)
    # Get customer
    response = client.get(f"/customers/{sample_customer_data['username']}")
    assert response.status_code == 200
    assert response.json()["username"] == sample_customer_data["username"]

def test_update_customer(test_db, sample_customer_data):
    # Create customer first
    client.post("/customers/", json=sample_customer_data)
    
    # Update customer
    update_data = {"full_name": "John Smith", "age": 31}
    response = client.put(
        f"/customers/{sample_customer_data['username']}", 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Smith"
    assert response.json()["age"] == 31

def test_wallet_operations(test_db, sample_customer_data):
    # Create customer first
    client.post("/customers/", json=sample_customer_data)
    
    # Test charging wallet
    charge_response = client.post(
        f"/customers/{sample_customer_data['username']}/charge",
        params={"amount": 100.0}
    )
    assert charge_response.status_code == 200
    assert "100.0" in charge_response.json()["message"]
    
    # Test deducting from wallet
    deduct_response = client.post(
        f"/customers/{sample_customer_data['username']}/deduct",
        params={"amount": 50.0}
    )
    assert deduct_response.status_code == 200
    assert "50.0" in deduct_response.json()["message"]