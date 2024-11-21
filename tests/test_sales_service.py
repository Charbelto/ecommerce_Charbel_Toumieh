import pytest
from fastapi.testclient import TestClient
from services.sales.sales_service import app
from unittest.mock import patch
from unittest.mock import Mock, patch
from unittest.mock import AsyncMock
import httpx
client = TestClient(app)

@pytest.fixture
def sample_purchase_data():
    return {
        "customer_username": "testuser",
        "item_id": 1,
        "quantity": 2
    }

@pytest.fixture
def mock_external_services(monkeypatch):
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json_data = json_data
        
        async def json(self):
            return self._json_data
    
    async def mock_get(*args, **kwargs):
        if "customers" in str(args):
            return MockResponse(
                status_code=200,
                json_data={"wallet_balance": 1000.0}
            )
        return MockResponse(
            status_code=200,
            json_data={
                "id": 1,
                "name": "Test Item",
                "price": 100.0,
                "stock": 10,
                "category": "test",
                "description": "Test description",
                "username": "seller1"
            }
        )
    
    get_mock = AsyncMock(side_effect=mock_get)
    post_mock = AsyncMock(return_value=MockResponse(200, {"message": "Success"}))
    
    with monkeypatch.context() as m:
        m.setattr(httpx.AsyncClient, "get", get_mock)
        m.setattr(httpx.AsyncClient, "post", post_mock)
        yield get_mock, post_mock

def test_make_purchase(test_db, sample_purchase_data, mock_external_services):
    response = client.post("/sales/", json=sample_purchase_data)
    assert response.status_code == 200
    assert "id" in response.json()  # Changed from "purchase_id" to "id"

def test_get_customer_purchases(test_db, sample_purchase_data, mock_external_services):
    # Make a purchase first
    client.post("/sales/", json=sample_purchase_data)
    
    # Get purchase history
    response = client.get(f"/purchases/{sample_purchase_data['customer_username']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)