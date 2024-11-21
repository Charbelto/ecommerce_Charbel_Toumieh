import pytest
from fastapi.testclient import TestClient
from services.sales.sales_service import app
import httpx
from unittest.mock import patch, Mock

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
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        async def mock_json():
            url = mock_get.call_args[0][0]
            if "items" in url:
                return {
                    "id": 1,
                    "name": "Test Item",
                    "price": 99.99,
                    "stock_count": 10,
                    "category": "test",
                    "description": "A test item"
                }
            elif "customers" in url:
                return {
                    "username": "johndoe",
                    "wallet_balance": 1000.0
                }
            return {}

        mock_response.json = mock_json
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
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
        async def mock_json():
            # Return different responses based on the URL
            if "customers" in mock_get.call_args[0][0]:
                return {
                    "username": "johndoe",
                    "wallet_balance": 1.0
                }
            elif "items" in mock_get.call_args[0][0]:
                return {
                    "id": 1,
                    "name": "Test Item",
                    "category": "electronics",
                    "price": 99.99,
                    "description": "A test item",
                    "stock_count": 10
                }
            
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = mock_json
        mock_get.return_value = mock_response
        
        response = client.post("/sales/", json=sample_purchase_data)
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]