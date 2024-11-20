import pytest
from fastapi.testclient import TestClient
from services.reviews.reviews_service import app
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def sample_review_data():
    return {
        "rating": 4.5,
        "comment": "Great product!",
        "item_id": 1
    }

@pytest.fixture
def mock_external_services():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,
            "name": "Test Product"
        }
        yield mock_get

def test_create_review(test_db, sample_review_data, mock_external_services):
    response = client.post(
        "/reviews/",
        json=sample_review_data,
        params={"customer_username": "johndoe"}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == sample_review_data["rating"]
    assert response.json()["comment"] == sample_review_data["comment"]

def test_get_product_reviews(test_db, sample_review_data, mock_external_services):
    # Create review first
    client.post(
        "/reviews/",
        json=sample_review_data,
        params={"customer_username": "johndoe"}
    )
    
    # Get reviews
    response = client.get(f"/reviews/product/{sample_review_data['item_id']}")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_update_review(test_db, sample_review_data, mock_external_services):
    # Create review first
    create_response = client.post(
        "/reviews/",
        json=sample_review_data,
        params={"customer_username": "johndoe"}
    )
    review_id = create_response.json()["id"]
    
    # Update review
    update_data = {"rating": 5.0, "comment": "Even better than I thought!"}
    response = client.put(
        f"/reviews/{review_id}",
        json=update_data,
        params={"customer_username": "johndoe"}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0
    assert response.json()["comment"] == "Even better than I thought!"

def test_moderate_review(test_db, sample_review_data, mock_external_services):
    # Create review first
    create_response = client.post(
        "/reviews/",
        json=sample_review_data,
        params={"customer_username": "johndoe"}
    )
    review_id = create_response.json()["id"]
    
    # Moderate review
    moderation_data = {
        "status": "approved",
        "moderation_comment": "Approved by moderator"
    }
    response = client.put(
        f"/reviews/{review_id}/moderate",
        json=moderation_data,
        params={"is_admin": True}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"