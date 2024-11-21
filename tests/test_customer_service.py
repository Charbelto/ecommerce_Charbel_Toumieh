import pytest
from fastapi.testclient import TestClient
from services.customer.customer_service import app, Customer

client = TestClient(app)

@pytest.fixture
def sample_customer_data():
    return {
        "username": "charbeltoumieh",
        "full_name": "Charbel Toumieh",
        "email": "charbel@example.com",
        "password": "password123",
        "address": "123 Test St",
        "age": 30,
        "gender": "male",
        "marital_status": "single",
        "phone": "1234567890",
        "wallet_balance": 0.0,
        "is_active": True,
        "role": "customer",
        "preferences": {}
    }

def test_create_customer(test_db, sample_customer_data):
    # Clean up any existing data
    test_db.query(Customer).delete()
    test_db.commit()
    
    response = client.post("/customers/", json=sample_customer_data)
    assert response.status_code == 200
    assert response.json()["username"] == sample_customer_data["username"]

def test_create_duplicate_customer(test_db, sample_customer_data):
    # Clean up any existing data
    test_db.query(Customer).delete()
    test_db.commit()
    
    # Create first customer
    client.post("/customers/", json=sample_customer_data)
    # Try to create duplicate
    response = client.post("/customers/", json=sample_customer_data)
    assert response.status_code == 400

def test_get_customer(test_db, sample_customer_data):
    # Clean up any existing data
    test_db.query(Customer).delete()
    test_db.commit()
    
    # Create customer first
    create_response = client.post("/customers/", json=sample_customer_data)
    assert create_response.status_code == 200
    
    # Get customer
    response = client.get(f"/customers/{sample_customer_data['username']}")
    assert response.status_code == 200
    assert response.json()["username"] == sample_customer_data["username"]

def test_update_customer(test_db, sample_customer_data):
    # Clean up any existing data
    test_db.query(Customer).delete()
    test_db.commit()
    
    # Create customer first
    create_response = client.post("/customers/", json=sample_customer_data)
    assert create_response.status_code == 200
    
    # Update customer
    update_data = {"full_name": "Updated Name", "age": 31}
    response = client.put(
        f"/customers/{sample_customer_data['username']}", 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["age"] == 31

def test_wallet_operations(test_db, sample_customer_data):
    # Clean up any existing data
    test_db.query(Customer).delete()
    test_db.commit()
    
    # Create customer first
    create_response = client.post("/customers/", json=sample_customer_data)
    assert create_response.status_code == 200
    
    # Test charging wallet
    charge_amount = 100.0
    charge_response = client.post(
        f"/customers/{sample_customer_data['username']}/charge",
        params={"amount": charge_amount}
    )
    assert charge_response.status_code == 200
    assert "successfully" in charge_response.json()["message"]