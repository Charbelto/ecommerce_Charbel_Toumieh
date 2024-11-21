from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, validator, ConfigDict, field_validator
from datetime import datetime
import httpx
from typing import List, Optional
from enum import Enum
import re
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import Review, Base
from .database import engine, SessionLocal
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base  # Updated import
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, validator, ConfigDict, field_validator
from datetime import datetime
import httpx
from typing import List, Optional
from enum import Enum
import re
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import Review, Base
from .database import engine, SessionLocal

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./reviews.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Service URLs
CUSTOMER_SERVICE_URL = "http://localhost:8000"
INVENTORY_SERVICE_URL = "http://localhost:8001"

# Review Status Enum
class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"

# Database Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_username = Column(String, index=True)
    item_id = Column(Integer, index=True)
    rating = Column(Float)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default=ReviewStatus.PENDING)
    moderation_comment = Column(String, nullable=True)

# Pydantic Models
class ReviewBase(BaseModel):
    rating: float = Field(
        ge=1, 
        le=5, 
        description="Rating must be between 1 and 5"
    )
    comment: str = Field(
        min_length=1,
        max_length=1000,
        pattern=r"^[a-zA-Z0-9\s.,!?-]*$",
        description="Review comment with allowed characters"
    )

    @field_validator('comment')
    @classmethod
    def sanitize_comment(cls, v: str) -> str:
        # Remove any potential HTML tags
        v = re.sub('<[^<]+?>', '', v)
        # Additional sanitization as needed
        return v.strip()

class ReviewCreate(BaseModel):
    item_id: int
    rating: float = Field(ge=1, le=5)
    comment: str = Field(min_length=10, max_length=1000)
    
    @field_validator('comment')
    def validate_comment(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Comment must be at least 10 characters long')
        # Remove any potential HTML tags
        v = re.sub('<[^<]+?>', '', v)
        return v.strip()
    
    model_config = ConfigDict(from_attributes=True)

class ReviewUpdate(ReviewBase):
    pass

class ReviewModeration(BaseModel):
    status: ReviewStatus
    moderation_comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: int
    customer_username: str
    item_id: int
    created_at: datetime
    updated_at: datetime
    status: ReviewStatus
    moderation_comment: Optional[str]
    
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

# Helper functions
async def verify_customer(username: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CUSTOMER_SERVICE_URL}/customers/{username}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Customer not found")

async def verify_item(item_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INVENTORY_SERVICE_URL}/items/{item_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Item not found")

# API Endpoints
@app.post("/reviews/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    customer_username: str,
    db: Session = Depends(get_db)
):
    """Submit a new review for a product"""
    # Verify customer and item exist
    await verify_customer(customer_username)
    await verify_item(review.item_id)
    
    # Check if user already reviewed this item
    existing_review = db.query(Review).filter(
        Review.customer_username == customer_username,
        Review.item_id == review.item_id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this item")
    
    db_review = Review(
        customer_username=customer_username,
        **review.dict()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    customer_username: str,
    db: Session = Depends(get_db)
):
    """Update an existing review"""
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if db_review.customer_username != customer_username:
        raise HTTPException(status_code=403, detail="Not authorized to update this review")
    
    for key, value in review_update.dict().items():
        setattr(db_review, key, value)
    
    db_review.updated_at = datetime.utcnow()
    db_review.status = ReviewStatus.PENDING  # Reset status for re-moderation
    db.commit()
    db.refresh(db_review)
    return db_review

@app.delete("/reviews/{review_id}")
async def delete_review(
    review_id: int,
    customer_username: str,
    is_admin: bool = False,
    db: Session = Depends(get_db)
):
    """Delete a review"""
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if not is_admin and db_review.customer_username != customer_username:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    
    db.delete(db_review)
    db.commit()
    return {"message": "Review deleted successfully"}

@app.get("/reviews/product/{item_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    item_id: int,
    status: Optional[ReviewStatus] = ReviewStatus.APPROVED,
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific product"""
    query = db.query(Review).filter(Review.item_id == item_id)
    if status:
        query = query.filter(Review.status == status)
    return query.all()

@app.get("/reviews/customer/{customer_username}", response_model=List[ReviewResponse])
async def get_customer_reviews(
    customer_username: str,
    db: Session = Depends(get_db)
):
    """Get all reviews by a specific customer"""
    return db.query(Review).filter(Review.customer_username == customer_username).all()

@app.put("/reviews/{review_id}/moderate", response_model=ReviewResponse)
async def moderate_review(
    review_id: int,
    moderation: ReviewModeration,
    is_admin: bool = True,  # In production, this should be properly authenticated
    db: Session = Depends(get_db)
):
    """Moderate a review (admin only)"""
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can moderate reviews")
    
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db_review.status = moderation.status
    db_review.moderation_comment = moderation.moderation_comment
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review_details(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific review"""
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

# Additional useful endpoints
@app.get("/reviews/product/{item_id}/stats")
async def get_product_review_stats(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Get statistical information about product reviews"""
    reviews = db.query(Review).filter(
        Review.item_id == item_id,
        Review.status == ReviewStatus.APPROVED
    ).all()
    
    if not reviews:
        return {
            "average_rating": 0,
            "total_reviews": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    ratings = [r.rating for r in reviews]
    rating_dist = {i: ratings.count(i) for i in range(1, 6)}
    
    return {
        "average_rating": sum(ratings) / len(ratings),
        "total_reviews": len(reviews),
        "rating_distribution": rating_dist
    }