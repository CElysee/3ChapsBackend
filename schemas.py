from datetime import datetime, time
from typing import Optional, List, Text

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    password: str
    gender: str
    country_id: Optional[int]
    role: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    gender: str
    country_id: int
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime
    updated_at: datetime


class UserCheck(BaseModel):
    email: EmailStr


class UserId(BaseModel):
    id: int


class FoodItemCategoriesCreate(BaseModel):
    category_name: str
    category_image: Text
    category_status: str
    category_description: Text
    created_at: datetime
    updated_at: Optional[datetime] = None
