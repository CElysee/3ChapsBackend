from datetime import datetime, time
from typing import Optional, List, Text

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[EmailStr]
    phone_number: str
    first_name: str
    last_name: str
    password: str
    gender: str
    country_id: Optional[int]
    is_active: Optional[bool] = True
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


class FoodItemCategoryCreate(BaseModel):
    category_name: str
    category_image: Text
    category_status: str
    category_description: Text
    created_at: Optional[datetime] = None


class FoodItemCreate(BaseModel):
    food_item_name: str
    food_item_description: Optional[Text] = None
    food_item_price: str
    food_item_status: Optional[str]
    food_item_type: Optional[str] = None
    isFeatured: str
    food_category_id: List[str] = []
    food_ingredient_id: List[str] = []
    food_modifier_id: List[str] = []
    created_at: Optional[datetime] = None


class FoodItemUpdate(BaseModel):
    food_item_name: Optional[str] = None
    food_item_description: Optional[Text] = None
    food_item_price: Optional[str] = None
    food_item_status: Optional[str] = None
    food_item_type: Optional[str] = None
    isFeatured: Optional[str] = None
    food_category_id: List[str] = []
    food_ingredient_id: List[str] = []
    food_modifier_id: List[str] = []
    updated_at: Optional[datetime] = None