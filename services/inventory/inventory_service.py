from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.orm import declarative_base  # Updated import
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
import enum
from typing import Optional
from sqlalchemy import Index
from utils.cache import cache_response, invalidate_cache
from pydantic import ConfigDict
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import Item, Base
from .database import engine, SessionLocal

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enum for Item Categories
class Category(str, enum.Enum):
    FOOD = "food"
    CLOTHES = "clothes"
    ACCESSORIES = "accessories"
    ELECTRONICS = "electronics"

# Database Model
class Item(Base):
    """
    Item database model representing products in inventory.

    Attributes:
        id (int): Primary key
        name (str): Product name
        category (Category): Product category (enum)
        price (float): Product price
        description (str): Product description
        stock_count (int): Current stock level
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    stock_count = Column(Integer, default=0, index=True)

    # Add composite index for common queries
    __table_args__ = (
        Index('idx_category_price', 'category', 'price'),
    )

# Pydantic Models
class ItemBase(BaseModel):
    name: str
    category: Category
    price: float = Field(gt=0)
    description: str
    stock_count: int = Field(ge=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[Category] = None
    price: Optional[float] = Field(gt=0, default=None)
    description: Optional[str] = None
    stock_count: Optional[int] = Field(ge=0, default=None)

class ItemResponse(ItemBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# API Endpoints
@app.post("/items/", response_model=ItemResponse)
@cache_response(expire_time_seconds=300)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item in inventory.

    Creates a new product entry with the specified details and initial stock count.
    Validates category and price information before creation.

    Args:
        item (ItemCreate): The item data to be created
        db (Session): Database session

    Returns:
        ItemResponse: The created item with additional fields

    Raises:
        HTTPException: 
            - 400: Invalid category or price
            - 422: Validation error

    Example:
        >>> item_data = {
        ...     "name": "Smartphone",
        ...     "category": "electronics",
        ...     "price": 599.99,
        ...     "stock_count": 100
        ... }
        >>> response = await create_item(item_data)
    """
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
@cache_response(expire_time_seconds=300)
async def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    
    # Invalidate cache after update
    invalidate_cache(f"get_item:{item_id}:*")
    return db_item

@app.post("/items/{item_id}/deduct")
def deduct_from_stock(item_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db_item.stock_count < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    db_item.stock_count -= quantity
    db.commit()
    return {"message": f"Stock updated successfully. New stock count: {db_item.stock_count}"}

# Additional useful endpoints
@app.get("/items/", response_model=list[ItemResponse])
def get_all_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

@app.get("/items/{item_id}", response_model=ItemResponse)
@cache_response(expire_time_seconds=300)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve item details by ID.

    Fetches complete item information including current stock level.
    Uses Redis caching for improved performance.

    Args:
        item_id (int): The ID of the item to retrieve
        db (Session): Database session

    Returns:
        ItemResponse: Complete item details

    Raises:
        HTTPException: 404 if item not found
    """
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

@app.post("/items/{item_id}/add-stock")
def add_to_stock(item_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.stock_count += quantity
    db.commit()
    return {"message": f"Stock updated successfully. New stock count: {db_item.stock_count}"}
