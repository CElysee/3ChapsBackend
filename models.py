from datetime import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    phone_number = Column(String(50), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    password = Column(String(250))
    gender = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_login = Column(DateTime)
    deleted = Column(Boolean)

    country = relationship("Country", back_populates="user")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    code = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="country")


class FoodItemCategories(Base):
    __tablename__ = "food_item_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50))
    category_image = Column(Text())
    category_status = Column(String(50))
    category_description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    food_items = relationship("FoodItems", back_populates="food_item_categories")


class FoodIngredients(Base):
    __tablename__ = "food_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_name = Column(String(50))
    ingredient_image = Column(Text())
    ingredient_status = Column(String(50))
    ingredient_description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    food_items = relationship("FoodItems", back_populates="food_ingredients")


class FoodModifiers(Base):
    __tablename__ = "food_modifiers"

    id = Column(Integer, primary_key=True, index=True)
    modifier_name = Column(String(50))
    modifier_image = Column(Text())
    modifier_description = Column(Text)
    modifier_price = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    food_items = relationship("FoodItems", back_populates="food_modifiers")


class FoodItems(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    food_item_name = Column(String(50))
    food_item_image = Column(Text())
    food_item_description = Column(Text)
    food_item_price = Column(String(50))
    food_item_status = Column(String(50))
    food_item_type = Column(String(50))
    isFeatured = Column(String(50))
    food_item_category_id = Column(Integer, ForeignKey("food_item_categories.id"))
    food_item_ingredient_id = Column(Integer, ForeignKey("food_ingredients.id"))
    food_item_modifier_id = Column(Integer, ForeignKey("food_modifiers.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    food_item_categories = relationship("FoodItemCategories", back_populates="food_items")
    food_ingredients = relationship("FoodIngredients", back_populates="food_items")
    food_modifiers = relationship("FoodModifiers", back_populates="food_items")
