import os
import uuid
from datetime import datetime, timedelta
import calendar
import random
from typing import Annotated, Any, List
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from database import db_dependency, get_db
from models import FoodItems, FoodCategories, FoodIngredients, FoodModifiers, FoodItemCategory, FoodItemIngredient, FoodItemModifier
from UploadFile import FileHandler
from schemas import FoodItemCreate
import logging

router = APIRouter(
    tags=["FoodItem"],
    prefix='/food_item'
)

UPLOAD_FOLDER = "FoodItem"
logger = logging.getLogger(__name__)


@router.get("/all")
async def get_food_items(db: db_dependency):
    food_items = db.query(FoodItems).all()
    items = []

    for item in food_items:
        category_ids = [category.food_category_id for category in
                        db.query(FoodItemCategory).filter(FoodItemCategory.food_item_id == item.id).all()]
        categories = db.query(FoodCategories).filter(FoodCategories.id.in_(category_ids)).all()
        ingredient_ids = [ingredient.food_ingredient_id for ingredient in db.query(FoodItemIngredient).filter(FoodItemIngredient.food_item_id == item.id).all()]
        ingredients = db.query(FoodIngredients).filter(FoodIngredients.id.in_(ingredient_ids)).all()
        modifier_ids = [modifier.food_modifier_id for modifier in db.query(FoodItemModifier).filter(FoodItemModifier.food_item_id == item.id).all()]
        modifiers = db.query(FoodModifiers).filter(FoodModifiers.id.in_(modifier_ids)).all()
        items.append({"item": item, "categories": categories, "ingredients": ingredients, "modifiers": modifiers})

    return items

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_food_item(db: Session = Depends(get_db), item_request: FoodItemCreate = Depends(),
                          food_item_image: UploadFile = File(...)):
    # Check if Item exist
    check_item = db.query(FoodItems).filter(FoodItems.food_item_name == item_request.food_item_name).first()
    if check_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="food item already exists")

    try:
        # Use the file_handler to save an uploaded file
        file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)
        saved_filename = file_handler.save_uploaded_file(food_item_image)
        food_item = FoodItems(
            food_item_name=item_request.food_item_name,
            food_item_image=saved_filename,
            food_item_description=item_request.food_item_description,
            food_item_price=item_request.food_item_price,
            food_item_status=item_request.food_item_status,
            food_item_type=item_request.food_item_type,
            isFeatured=item_request.isFeatured,
            created_at=datetime.now(),
        )
        db.add(food_item)
        db.commit()

        if item_request.food_category_id:
            for category_id in item_request.food_category_id:
                food_category = FoodItemCategory(
                    food_item_id=food_item.id,
                    food_category_id=category_id,
                    created_at=datetime.now(),
                )
                db.add(food_category)
                db.commit()

        if item_request.food_ingredient_id:
            for ingredient_id in item_request.food_ingredient_id:
                food_ingredient = FoodItemIngredient(
                    food_item_id=food_item.id,
                    food_ingredient_id=ingredient_id,
                    created_at=datetime.now(),
                )
                db.add(food_ingredient)
                db.commit()

        if item_request.food_modifier_id:
            for modifier_id in item_request.food_modifier_id:
                food_modifier = FoodItemModifier(
                    food_item_id=food_item.id,
                    food_modifier_id=modifier_id,
                    created_at=datetime.now(),
                )
                db.add(food_modifier)
                db.commit()

        return {"message": "Food Item created successfully"}

    except Exception as e:
        db.rollback()
        error_msg = f"Error adding a new user: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
