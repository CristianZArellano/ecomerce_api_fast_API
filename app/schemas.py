from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Esquemas de Usuario
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Esquemas de Producto
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    is_available: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}