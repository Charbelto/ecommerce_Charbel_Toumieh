from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    age = Column(Integer)
    address = Column(String)
    gender = Column(String)
    marital_status = Column(String)
    wallet_balance = Column(Float, default=0.0)
    email = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="customer")
    preferences = Column(JSON, default={})