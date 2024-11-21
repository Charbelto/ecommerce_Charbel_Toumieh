from pydantic import BaseModel

class ItemBase(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str