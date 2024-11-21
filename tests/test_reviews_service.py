import pytest
from fastapi.testclient import TestClient
from services.reviews.reviews_service import app, Review
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from httpx import AsyncMock

client = TestClient(app)

@pytest.fixture
def sample_review_data():
    return {
        "item_id": 1,
        "rating": 5,
        "comment": "This is a detailed review of the product that I really enjoyed using! Great purchase.",
        "status": "PENDING"
    }

def test_create_review(test_db, sample_review_data, mock_external_services):
    # Clear the reviews table
    test_db.query(Review).delete()
    test_db.commit()
    
    # Only send the required fields in the request
    review_data = {
        "item_id": sample_review_data["item_id"],
        "rating": sample_review_data["rating"],
        "comment": sample_review_data["comment"]
    }
    
    response = client.post(
        "/reviews/",
        json=review_data,
        params={"customer_username": "testuser"}
    )
    
    print(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        print(f"Response body: {response.json()}")
    
    assert response.status_code == 200
    assert "id" in response.json()
    
    # Verify the review was created
    created_review = test_db.query(Review).first()
    assert created_review is not None
    assert created_review.customer_username == "testuser"
    assert created_review.item_id == sample_review_data["item_id"]

def test_get_product_reviews(test_db, sample_review_data, mock_external_services):
    response = client.get(f"/reviews/product/{sample_review_data['item_id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    
@pytest.fixture
def mock_external_services():
    async def mock_get(*args, **kwargs):
        response = Mock()
        response.status_code = 200
        if "customers" in str(args[0]):
            response.json.return_value = {
                "username": "testuser",
                "full_name": "Test User"
            }
        else:
            response.json.return_value = {
                "id": 1,
                "name": "Test Item"
            }
        return response

    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_get
        yield mock_get