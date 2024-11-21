from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, ConfigDict
class CustomerBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    age: int
    address: str
    gender: str
    marital_status: str
    phone: str
    
class CustomerCreate(CustomerBase):
    password: str
    preferences: Optional[Dict] = {}

class CustomerResponse(CustomerBase):
    id: int
    wallet_balance: float
    is_active: bool
    role: str
    
    model_config = ConfigDict(from_attributes=True)