from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    age = Column(Integer)
    address = Column(String)
    gender = Column(String)
    marital_status = Column(String)
    wallet_balance = Column(Float, default=0.0)
    email = Column(String, unique=True)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='customer')
    preferences = Column(String, default='{}')