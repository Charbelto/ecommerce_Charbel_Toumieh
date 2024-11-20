import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def test_db():
    # Create test database engine
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    from services.customer.customer_service import Base as CustomerBase
    from services.inventory.inventory_service import Base as InventoryBase
    from services.sales.sales_service import Base as SalesBase
    from services.reviews.reviews_service import Base as ReviewsBase
    
    CustomerBase.metadata.create_all(bind=engine)
    InventoryBase.metadata.create_all(bind=engine)
    SalesBase.metadata.create_all(bind=engine)
    ReviewsBase.metadata.create_all(bind=engine)
    
    # Create test database session
    db = TestingSessionLocal()
    yield db
    
    # Cleanup
    db.close()
    os.remove("./test.db")

@pytest.fixture
def mock_redis(mocker):
    mock_redis = mocker.patch('redis.Redis')
    return mock_redis