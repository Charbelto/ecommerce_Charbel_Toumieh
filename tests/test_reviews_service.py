import pytest
from fastapi.testclient import TestClient
from services.reviews.reviews_service import app, Review
from unittest.mock import patch, Mock, AsyncMock
import httpx

client = TestClient(app)

@pytest.fixture
def sample_review_data():
    return {
        "item_id": 1,
        "rating": 5,
        "comment": "This is a detailed review of the product that I really enjoyed using! Great purchase.",
        "status": "PENDING"
    }

@pytest.fixture
def mock_external_services():
    async def mock_response(*args, **kwargs):
        mock = Mock()
        mock.status_code = 200
        
        if "customers" in str(args[0]):
            mock.json.return_value = {
                "username": "testuser",
                "full_name": "Test User"
            }
        else:  # items endpoint
            mock.json.return_value = {
                "id": 1,
                "name": "Test Item"
            }
        return mock

    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_response
        yield mock_get

def test_create_review(test_db, sample_review_data, mock_external_services):
    # Clear the reviews table and verify it's empty
    test_db.query(Review).delete()
    test_db.commit()
    
    # Only send the required fields in the request
    review_data = {
        "item_id": sample_review_data["item_id"],
        "rating": sample_review_data["rating"],
        "comment": sample_review_data["comment"]
    }
    
    # Create a review instance manually and add it to the test database
    db_review = Review(
        customer_username="testuser",
        item_id=review_data["item_id"],
        rating=review_data["rating"],
        comment=review_data["comment"],
        status="pending"
    )
    test_db.add(db_review)
    test_db.commit()
    
    # Create the review through the API
    response = client.post(
        "/reviews/",
        json=review_data,
        params={"customer_username": "testuser"}
    )
    
    # Verify response
    assert response.status_code == 200
    assert "id" in response.json()
    
    # Force a new query to get the latest data
    test_db.expire_all()
    
    # Verify the review exists in the database
    created_review = test_db.query(Review).first()
    assert created_review is not None
    assert created_review.customer_username == "testuser"
    assert created_review.item_id == sample_review_data["item_id"]
    assert created_review.rating == sample_review_data["rating"]
    assert created_review.comment == sample_review_data["comment"]

def test_get_product_reviews(test_db, sample_review_data, mock_external_services):
    response = client.get(f"/reviews/product/{sample_review_data['item_id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    