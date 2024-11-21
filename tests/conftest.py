import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.customer.models.customer import Base as CustomerBase
from services.inventory.inventory_service import Base as InventoryBase
from services.reviews.reviews_service import Base as ReviewBase
from services.sales.sales_service import Base as SaleBase
from services.reviews.reviews_service import app
from services.reviews.database import SessionLocal

@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture(scope="function")
def test_db():
    # Create test database in memory
    engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    CustomerBase.metadata.create_all(engine)
    InventoryBase.metadata.create_all(engine)
    ReviewBase.metadata.create_all(engine)
    SaleBase.metadata.create_all(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    # Override the dependency
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[SessionLocal] = override_get_db
    
    yield db
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_customer_data():
    return {
        "full_name": "Test User",
        "username": "testuser",
        "password": "testpass123",
        "age": 30,
        "address": "123 Test St",
        "gender": "male",
        "marital_status": "single",
        "email": "test@example.com",
        "phone": "1234567890",
        "is_active": True,
        "role": "customer",
        "preferences": "{}"
    }

@pytest.fixture
def sample_purchase_data():
    return {
        "customer_username": "testuser",
        "item_id": 1,
        "quantity": 2
    }