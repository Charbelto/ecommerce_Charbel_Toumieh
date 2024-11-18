from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
import enum
from typing import Optional

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
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    price = Column(Float)
    description = Column(String)
    stock_count = Column(Integer, default=0)

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

    class Config:
        orm_mode = True

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
def add_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
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
def get_item(item_id: int, db: Session = Depends(get_db)):
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