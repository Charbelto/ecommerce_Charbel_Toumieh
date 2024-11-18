from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import httpx
from typing import List, Optional
from prometheus_client import Counter, Histogram, generate_latest
import time
from utils.exceptions import ResourceNotFoundException, InsufficientFundsException
from utils.version import VersionedAPI

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sales.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Service URLs
CUSTOMER_SERVICE_URL = "http://localhost:8000"
INVENTORY_SERVICE_URL = "http://localhost:8001"

# Database Models
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    customer_username = Column(String, index=True)
    item_id = Column(Integer)
    item_name = Column(String)
    quantity = Column(Integer)
    price_per_item = Column(Float)
    total_price = Column(Float)
    purchase_date = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ItemBase(BaseModel):
    id: int
    name: str
    price: float
    stock_count: Optional[int]
    category: Optional[str]
    description: Optional[str]

class ItemBrief(BaseModel):
    name: str
    price: float

class PurchaseRequest(BaseModel):
    customer_username: str
    item_id: int
    quantity: int = 1

class PurchaseResponse(BaseModel):
    id: int
    customer_username: str
    item_name: str
    quantity: int
    price_per_item: float
    total_price: float
    purchase_date: datetime

    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI()
versioned_api = VersionedAPI(app)

# Add version middleware
app.middleware("http")(versioned_api.version_middleware)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Version 1 endpoints
@versioned_api.version("v1")
@app.get("/sales/", response_model=List[PurchaseResponse])
async def list_sales_v1(db: Session = Depends(get_db)):
    return db.query(Purchase).all()

# Version 2 endpoints with enhanced features
@versioned_api.version("v2")
@app.get("/sales/", response_model=List[PurchaseResponse])
async def list_sales_v2(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "purchase_date"
):
    query = db.query(Purchase)
    if sort_by:
        query = query.order_by(getattr(Purchase, sort_by).desc())
    return query.offset(skip).limit(limit).all()

# Create tables
Base.metadata.create_all(bind=engine)

# Helper functions
async def get_customer_balance(username: str) -> float:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CUSTOMER_SERVICE_URL}/customers/{username}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Customer not found")
        return response.json()["wallet_balance"]

async def deduct_customer_balance(username: str, amount: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CUSTOMER_SERVICE_URL}/customers/{username}/deduct",
            params={"amount": amount}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to deduct money from wallet")

async def get_item_details(item_id: int) -> ItemBase:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INVENTORY_SERVICE_URL}/items/{item_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Item not found")
        return ItemBase(**response.json())

async def deduct_item_stock(item_id: int, quantity: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{INVENTORY_SERVICE_URL}/items/{item_id}/deduct",
            params={"quantity": quantity}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to update inventory")

async def process_purchase(purchase: PurchaseRequest, db: Session) -> Purchase:
    """
    Process a new purchase transaction.

    This function handles the complete purchase flow:
    1. Validates customer funds
    2. Checks item availability
    3. Creates purchase record
    4. Updates inventory
    5. Processes payment

    Args:
        purchase (PurchaseRequest): Purchase request containing customer and item details
        db (Session): Database session for transaction management

    Returns:
        Purchase: Created purchase record

    Raises:
        InsufficientFundsException: If customer has insufficient funds
        ResourceNotFoundException: If item or customer not found
    """
    # Get customer balance and item details
    balance = await get_customer_balance(purchase.customer_username)
    item = await get_item_details(purchase.item_id)
    total_cost = item.price * purchase.quantity
    
    # Verify funds and process payment
    if balance < total_cost:
        raise InsufficientFundsException(
            username=purchase.customer_username,
            required=total_cost,
            available=balance
        )
    
    await deduct_customer_balance(purchase.customer_username, total_cost)
    await deduct_item_stock(purchase.item_id, purchase.quantity)
    
    # Create and save purchase record
    db_purchase = Purchase(
        customer_username=purchase.customer_username,
        item_id=purchase.item_id,
        item_name=item.name,
        quantity=purchase.quantity,
        price_per_item=item.price,
        total_price=total_cost
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return db_purchase

# API Endpoints
@app.get("/items/", response_model=List[ItemBrief])
async def list_available_items():
    """Display available goods with basic information"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INVENTORY_SERVICE_URL}/items/")
        items = response.json()
        return [
            ItemBrief(name=item["name"], price=item["price"])
            for item in items
            if item["stock_count"] > 0
        ]

@app.get("/items/{item_id}", response_model=ItemBase)
async def get_item_details_api(item_id: int):
    """Get full details of a specific item"""
    return await get_item_details(item_id)

# Prometheus metrics
SALES_COUNTER = Counter('total_sales', 'Total number of sales')
REQUEST_TIME = Histogram('request_processing_seconds', 'Time spent processing request')

# Add this endpoint to expose metrics
@app.get("/metrics")
def metrics():
    return generate_latest()

# Modify the make_purchase endpoint to include metrics
@app.post("/sales/", response_model=PurchaseResponse)
async def make_purchase(purchase: PurchaseRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    try:
        result = await process_purchase(purchase, db)
        SALES_COUNTER.inc()
        return result
    finally:
        REQUEST_TIME.observe(time.time() - start_time)

@app.get("/purchases/{customer_username}", response_model=List[PurchaseResponse])
async def get_customer_purchases(customer_username: str, db: Session = Depends(get_db)):
    """Get purchase history for a customer"""
    purchases = db.query(Purchase).filter(
        Purchase.customer_username == customer_username
    ).order_by(Purchase.purchase_date.desc()).all()
    
    return purchases

# Example of using custom exceptions
@app.post("/sales/", response_model=PurchaseResponse)
async def make_purchase(purchase: PurchaseRequest, db: Session = Depends(get_db)):
    try:
        balance = await get_customer_balance(purchase.customer_username)
        item = await get_item_details(purchase.item_id)
        total_cost = item.price * purchase.quantity
        
        if balance < total_cost:
            raise InsufficientFundsException(
                username=purchase.customer_username,
                required=total_cost,
                available=balance
            )
            
        # Process purchase logic here...
        
    except HTTPException as e:
        if e.status_code == 404:
            raise ResourceNotFoundException(
                resource="item" if "Item" in str(e) else "customer",
                service="sales",
                resource_id=purchase.item_id if "Item" in str(e) else purchase.customer_username
            )
        raise