from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Purchase(Base):
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    product_id = Column(String, index=True)
    quantity = Column(Integer)
    total_price = Column(Float)
    purchase_date = Column(DateTime)