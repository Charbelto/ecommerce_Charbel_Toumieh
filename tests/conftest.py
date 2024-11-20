import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys
import time
from unittest.mock import patch
import fakeredis

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
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        # Wait a bit before trying to remove the file
        time.sleep(0.1)
        try:
            if os.path.exists("./test.db"):
                os.remove("./test.db")
        except PermissionError:
            pass  # Ignore permission errors during cleanup

@pytest.fixture(autouse=True)
def mock_redis():
    with patch('utils.cache.redis_client', fakeredis.FakeStrictRedis()):
        yield

@pytest.fixture
def mock_redis(mocker):
    mock_redis = mocker.patch('redis.Redis')
    return mock_redis