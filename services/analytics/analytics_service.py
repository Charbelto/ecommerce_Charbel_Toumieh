from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx
from typing import List, Dict
import asyncio
from utils.profiling_manager import ProfilingManager
from utils.profiling import performance_profile, track_memory_usage
import uuid
from utils.profiling_decorators import detailed_profile

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@analytics_db:5432/analytics_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Service URLs
CUSTOMER_SERVICE_URL = "http://customer_service:8000"
SALES_SERVICE_URL = "http://sales_service:8000"
INVENTORY_SERVICE_URL = "http://inventory_service:8000"

# Database Models
class SalesMetrics(Base):
    __tablename__ = "sales_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    total_revenue = Column(Float)
    total_orders = Column(Integer)
    average_order_value = Column(Float)

class CustomerMetrics(Base):
    __tablename__ = "customer_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    total_customers = Column(Integer)
    active_customers = Column(Integer)
    average_customer_age = Column(Float)

# Pydantic Models
class MetricsResponse(BaseModel):
    date: datetime
    total_revenue: float
    total_orders: int
    average_order_value: float
    total_customers: int
    active_customers: int
    average_customer_age: float
    top_selling_items: List[Dict]

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

async def fetch_sales_data(start_date: datetime, end_date: datetime) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SALES_SERVICE_URL}/sales/metrics",
            params={"start_date": start_date, "end_date": end_date}
        )
        return response.json()

async def fetch_customer_data() -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CUSTOMER_SERVICE_URL}/customers/metrics")
        return response.json()

async def fetch_inventory_data() -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INVENTORY_SERVICE_URL}/items/top-selling")
        return response.json()

"""
Analytics Service
===============

Provides real-time analytics and reporting capabilities for the e-commerce platform.

Features:
    - Real-time metrics calculation
    - Historical data analysis
    - Trend analysis
    - Customer behavior insights
    - Sales performance metrics

Dependencies:
    - PostgreSQL for metrics storage
    - Redis for caching
    - FastAPI for API endpoints
"""

profiling_manager = ProfilingManager()

@app.middleware("http")
async def profiling_middleware(request: Request, call_next):
    with profiling_manager.profile_request(request_id=str(uuid.uuid4())):
        response = await call_next(request)
        return response

@performance_profile(output_file="profile_results.prof")
@track_memory_usage
@detailed_profile(output_prefix="dashboard_metrics")
async def get_dashboard_metrics(
    time_range: str = "24h",
    db: Session = Depends(get_db)
) -> MetricsResponse:
    """
    Generate dashboard metrics for specified time range.

    Aggregates data from multiple services to provide comprehensive metrics including:
    - Total revenue
    - Order count
    - Average order value
    - Customer metrics
    - Top-selling items

    Args:
        time_range (str): Time range for metrics ("24h", "7d", "30d")
        db (Session): Database session

    Returns:
        MetricsResponse: Aggregated metrics data

    Raises:
        HTTPException: If time range is invalid
    """
    end_date = datetime.utcnow()
    
    if time_range == "24h":
        start_date = end_date - timedelta(days=1)
    elif time_range == "7d":
        start_date = end_date - timedelta(days=7)
    elif time_range == "30d":
        start_date = end_date - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid time range")

    # Fetch data from different services concurrently
    sales_data, customer_data, inventory_data = await asyncio.gather(
        fetch_sales_data(start_date, end_date),
        fetch_customer_data(),
        fetch_inventory_data()
    )

    # Store metrics in database
    metrics = SalesMetrics(
        date=end_date,
        total_revenue=sales_data["total_revenue"],
        total_orders=sales_data["total_orders"],
        average_order_value=sales_data["average_order_value"]
    )
    db.add(metrics)
    db.commit()

    return {
        "date": end_date,
        "total_revenue": sales_data["total_revenue"],
        "total_orders": sales_data["total_orders"],
        "average_order_value": sales_data["average_order_value"],
        "total_customers": customer_data["total_customers"],
        "active_customers": customer_data["active_customers"],
        "average_customer_age": customer_data["average_age"],
        "top_selling_items": inventory_data["top_items"]
    }

@app.get("/analytics/trends")
async def get_trends(
    metric: str,
    time_range: str = "30d",
    db: Session = Depends(get_db)
):
    """Get historical trends for specific metrics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=int(time_range.replace("d", "")))

    if metric == "sales":
        data = db.query(
            func.date_trunc('day', SalesMetrics.date).label('date'),
            func.sum(SalesMetrics.total_revenue).label('total_revenue')
        ).filter(
            SalesMetrics.date.between(start_date, end_date)
        ).group_by(
            func.date_trunc('day', SalesMetrics.date)
        ).all()
        
        return [{"date": row.date, "value": row.total_revenue} for row in data]

    raise HTTPException(status_code=400, detail="Invalid metric specified")