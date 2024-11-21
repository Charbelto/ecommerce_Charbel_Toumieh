from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum, Boolean, JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ConfigDict
import enum
from typing import Optional, List

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./customers.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums for Gender and Marital Status
class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class MaritalStatus(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

# Database Model
class Customer(Base):
    """
    Customer database model representing the customers table.

    Attributes:
        id (int): Primary key
        full_name (str): Customer's full name
        username (str): Unique username for identification
        password (str): Hashed password (in production)
        age (int): Customer's age
        address (str): Customer's address
        gender (Gender): Customer's gender (enum)
        marital_status (MaritalStatus): Customer's marital status (enum)
        wallet_balance (float): Current wallet balance
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # In production, this should be hashed
    age = Column(Integer)
    address = Column(String)
    gender = Column(String)
    marital_status = Column(String)
    wallet_balance = Column(Float, default=0.0)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="customer")
    preferences = Column(JSON, default={})

# Pydantic Models for Request/Response
class CustomerBase(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
    address: str | None = None
    age: int | None = None
    gender: str | None = None
    marital_status: str | None = None
    phone: str | None = None
    wallet_balance: float = 0.0
    is_active: bool = True
    role: str = "customer"
    preferences: dict = {}
    
    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None

class CustomerResponse(CustomerBase):
    id: int
    wallet_balance: float

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
@app.post("/customers/", response_model=CustomerResponse)
def create_customer(customer: CustomerBase, db: Session = Depends(get_db)):
    db_customer = Customer(**customer.model_dump())
    try:
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

@app.delete("/customers/{username}")
def delete_customer(username: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

@app.put("/customers/{username}", response_model=CustomerResponse)
def update_customer(username: str, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.username == username).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers/", response_model=List[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@app.get("/customers/{username}", response_model=CustomerResponse)
def get_customer(username: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/customers/{username}/charge")
def charge_wallet(username: str, amount: float, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == username).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.wallet_balance += amount
    db.commit()
    return {"message": "Wallet charged successfully", "new_balance": customer.wallet_balance}

@app.post("/customers/{username}/deduct")
def deduct_from_wallet(username: str, amount: float, db: Session = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    customer = db.query(Customer).filter(Customer.username == username).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer.wallet_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    customer.wallet_balance -= amount
    db.commit()
    return {"message": f"Amount deducted successfully. New balance: ${customer.wallet_balance}"}