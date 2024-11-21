import pytest
from fastapi.testclient import TestClient
from services.customer.customer_service import app, Customer

client = TestClient(app)

@pytest.fixture
def sample_customer_data():
    return {
        "username": "ctoumieh",
        "full_name": "Charbel Toumieh",
        "email": "charbel@example.com",
        "password": "securepass123",
        "address": "123 Cedar St",
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
    test_db.query(Customer).delete()
    test_db.commit()
    
    response = client.post("/customers/", json=sample_customer_data)
    assert response.status_code == 200
    assert response.json()["username"] == sample_customer_data["username"]

def test_get_customer(test_db, sample_customer_data):
    response = client.get(f"/customers/{sample_customer_data['username']}")
    assert response.status_code == 200
    assert response.json()["username"] == sample_customer_data["username"]

def test_update_customer(test_db, sample_customer_data):
    update_data = {"full_name": "Updated Name", "age": 31}
    response = client.put(
        f"/customers/{sample_customer_data['username']}", 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"