from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

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