import pytest
from fastapi.testclient import TestClient
from services.inventory.inventory_service import app
from sqlalchemy import Index
from utils.cache import cache_response, invalidate_cache


client = TestClient(app)

@pytest.fixture
def sample_item_data():
    return {
        "name": "Test Item",
        "category": "electronics",
        "price": 99.99,
        "description": "A test item",
        "stock_count": 10
    }

def test_add_item(test_db, sample_item_data):
    response = client.post("/items/", json=sample_item_data)
    assert response.status_code == 200
    assert response.json()["name"] == sample_item_data["name"]
    assert response.json()["stock_count"] == sample_item_data["stock_count"]

def test_get_item(test_db, sample_item_data):
    # Add item first
    create_response = client.post("/items/", json=sample_item_data)
    item_id = create_response.json()["id"]
    
    # Get item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_item_data["name"]

def test_update_item(test_db, sample_item_data):
    # Add item first
    create_response = client.post("/items/", json=sample_item_data)
    item_id = create_response.json()["id"]
    
    # Update item
    update_data = {"price": 89.99, "stock_count": 15}
    response = client.put(f"/items/{item_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["price"] == 89.99
    assert response.json()["stock_count"] == 15

def test_deduct_stock(test_db, sample_item_data):
    # Add item first
    create_response = client.post("/items/", json=sample_item_data)
    item_id = create_response.json()["id"]
    
    # Deduct stock
    response = client.post(f"/items/{item_id}/deduct", params={"quantity": 3})
    assert response.status_code == 200
    assert "7" in response.json()["message"]  # New stock count should be 7

def test_insufficient_stock(test_db, sample_item_data):
    # Add item first
    create_response = client.post("/items/", json=sample_item_data)
    item_id = create_response.json()["id"]
    
    # Try to deduct more than available
    response = client.post(f"/items/{item_id}/deduct", params={"quantity": 20})
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]