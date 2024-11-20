import pytest
from fastapi.testclient import TestClient
from services.sales.sales_service import app
import httpx
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def sample_purchase_data():
    return {
        "customer_username": "johndoe",
        "item_id": 1,
        "quantity": 2
    }

@pytest.fixture
def mock_external_services():
    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('httpx.AsyncClient.post') as mock_post:
        # Mock customer service responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "username": "johndoe",
            "wallet_balance": 1000.0
        }
        
        # Mock inventory service responses
        mock_post.return_value.status_code = 200
        yield mock_get, mock_post

def test_make_purchase(test_db, sample_purchase_data, mock_external_services):
    response = client.post("/sales/", json=sample_purchase_data)
    assert response.status_code == 200
    assert response.json()["customer_username"] == sample_purchase_data["customer_username"]
    assert response.json()["quantity"] == sample_purchase_data["quantity"]

def test_get_customer_purchases(test_db, sample_purchase_data, mock_external_services):
    # Make a purchase first
    client.post("/sales/", json=sample_purchase_data)
    
    # Get purchase history
    response = client.get(f"/purchases/{sample_purchase_data['customer_username']}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["customer_username"] == sample_purchase_data["customer_username"]

@pytest.mark.asyncio
async def test_process_purchase_insufficient_funds(test_db, sample_purchase_data):
    with patch('httpx.AsyncClient.get') as mock_get:
        # Mock customer with insufficient funds
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "username": "johndoe",
            "wallet_balance": 1.0
        }
        
        response = client.post("/sales/", json=sample_purchase_data)
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]