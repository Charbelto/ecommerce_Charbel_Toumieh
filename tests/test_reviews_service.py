import pytest
from fastapi.testclient import TestClient
from services.reviews.reviews_service import app, Review
from unittest.mock import patch, Mock

client = TestClient(app)

@pytest.fixture
def sample_review_data():
    return {
        "item_id": 1,
        "rating": 4.5,
        "comment": "Great product!"
    }

@pytest.fixture
def mock_external_services():
    with patch('httpx.AsyncClient.get') as mock_get:
        async def mock_json():
            return {
                "id": 1,
                "name": "Test Item",
                "price": 99.99,
                "stock_count": 10
            }
            
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = mock_json
        mock_get.return_value = mock_response
        yield mock_get

def test_create_review(test_db, sample_review_data, mock_external_services):
    # Clean up existing reviews
    test_db.query(Review).delete()
    test_db.commit()
    
    headers = {
        "X-Auth-Token": "test_token",
        "Content-Type": "application/json"
    }
    
    # First verify the item exists
    item_response = client.get(f"/items/{sample_review_data['item_id']}")
    assert item_response.status_code == 200
    
    response = client.post(
        "/reviews/",
        json=sample_review_data,
        params={"customer_username": "charbeltoumieh"},
        headers=headers
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_product_reviews(test_db, sample_review_data, mock_external_services):
    # Clean up existing reviews
    test_db.query(Review).delete()
    test_db.commit()
    
    # Create review first
    headers = {"X-Auth-Token": "test_token"}
    create_response = client.post(
        "/reviews/",
        json=sample_review_data,
        params={"customer_username": "charbeltoumieh"},
        headers=headers
    )
    assert create_response.status_code == 200
    
    # Get reviews
    response = client.get(f"/reviews/product/{sample_review_data['item_id']}")
    assert response.status_code == 200
    assert len(response.json()) > 0