import os
import uuid
from datetime import datetime, timedelta
import calendar
import random
from typing import Annotated, Any, List
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from database import db_dependency, get_db
from models import FoodItems, FoodCategories, FoodIngredients, FoodModifiers, FoodItemCategory, FoodItemIngredient, \
    FoodItemModifier
from UploadFile import FileHandler
from schemas import FoodItemCreate, FoodItemUpdate
import logging

router = APIRouter(
    tags=["FoodItem"],
    prefix='/food_item'
)

UPLOAD_FOLDER = "FoodItem"
logger = logging.getLogger(__name__)


def jsonToList(data):
    string_value = data[0]
    # Split the string into a list of integers
    return [int(category_id) for category_id in string_value.split(',')]


@router.get("/all")
async def get_food_items(db: db_dependency):
    food_items = db.query(FoodItems).all()
    items = []

    for item in food_items:
        category_ids = [category.food_category_id for category in
                        db.query(FoodItemCategory).filter(FoodItemCategory.food_item_id == item.id).all()]
        categories = db.query(FoodCategories).filter(FoodCategories.id.in_(category_ids)).all()
        ingredient_ids = [ingredient.food_ingredient_id for ingredient in
                          db.query(FoodItemIngredient).filter(FoodItemIngredient.food_item_id == item.id).all()]
        ingredients = db.query(FoodIngredients).filter(FoodIngredients.id.in_(ingredient_ids)).all()
        modifier_ids = [modifier.food_modifier_id for modifier in
                        db.query(FoodItemModifier).filter(FoodItemModifier.food_item_id == item.id).all()]
        modifiers = db.query(FoodModifiers).filter(FoodModifiers.id.in_(modifier_ids)).all()
        items.append({"item": item, "categories": categories, "ingredients": ingredients, "modifiers": modifiers})

    return items


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_food_item(db: Session = Depends(get_db), item_request: FoodItemCreate = Depends(),
                           food_item_image: UploadFile = File(...)):
    # Convert the JSON string to a list of integers
    food_category_ids = jsonToList(item_request.food_category_id)
    food_ingredient_ids = jsonToList(item_request.food_ingredient_id)
    food_modifier_ids = jsonToList(item_request.food_modifier_id)

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

        if food_category_ids:
            for category_id in food_category_ids:
                food_category = FoodItemCategory(
                    food_item_id=food_item.id,
                    food_category_id=category_id,
                    created_at=datetime.now(),
                )
                db.add(food_category)
                db.commit()

        if food_ingredient_ids:
            for ingredient_id in food_ingredient_ids:
                food_ingredient = FoodItemIngredient(
                    food_item_id=food_item.id,
                    food_ingredient_id=ingredient_id,
                    created_at=datetime.now(),
                )
                db.add(food_ingredient)
                db.commit()

        if food_modifier_ids:
            for modifier_id in food_modifier_ids:
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


@router.get("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_food_item(id: int, db: db_dependency):
    food_item = db.query(FoodItems).filter(FoodItems.id == id).first()
    if food_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")
    item = []
    category_ids = [category.food_category_id for category in
                    db.query(FoodItemCategory).filter(FoodItemCategory.food_item_id == food_item.id).all()]
    categories = db.query(FoodCategories).filter(FoodCategories.id.in_(category_ids)).all()
    ingredient_ids = [ingredient.food_ingredient_id for ingredient in
                      db.query(FoodItemIngredient).filter(FoodItemIngredient.food_item_id == food_item.id).all()]
    ingredients = db.query(FoodIngredients).filter(FoodIngredients.id.in_(ingredient_ids)).all()
    modifier_ids = [modifier.food_modifier_id for modifier in
                    db.query(FoodItemModifier).filter(FoodItemModifier.food_item_id == food_item.id).all()]
    modifiers = db.query(FoodModifiers).filter(FoodModifiers.id.in_(modifier_ids)).all()
    item.append({"item": food_item, "categories": categories, "ingredients": ingredients, "modifiers": modifiers})
    return item


@router.put("/update/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_food_item(id: int, db: db_dependency, item_request: FoodItemUpdate = Depends(),
                           food_item_image: UploadFile = File(None)):
    # Convert the JSON string to a list of integers
    food_category_ids = jsonToList(item_request.food_category_id)
    food_ingredient_ids = jsonToList(item_request.food_ingredient_id)
    food_modifier_ids = jsonToList(item_request.food_modifier_id)

    food_item_update = db.query(FoodItems).filter(FoodItems.id == id).first()
    if food_item_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")
    try:
        # Use the file_handler to save an uploaded file
        if food_item_image:
            file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)
            saved_filename = file_handler.save_uploaded_file(food_item_image)
            food_item_update.food_item_image = saved_filename
        if item_request.food_item_name:
            food_item_update.food_item_name = item_request.food_item_name
        if item_request.food_item_description:
            food_item_update.food_item_description = item_request.food_item_description
        if item_request.food_item_price:
            food_item_update.food_item_price = item_request.food_item_price
        if item_request.food_item_status:
            food_item_update.food_item_status = item_request.food_item_status
        if item_request.food_item_type:
            food_item_update.food_item_type = item_request.food_item_type
        if item_request.isFeatured:
            food_item_update.isFeatured = item_request.isFeatured
        if item_request.updated_at:
            food_item_update.updated_at = datetime.now()
        db.commit()

        try:
            for category_id in food_category_ids:
                check_if_exist = db.query(FoodItemCategory).filter(
                    FoodItemCategory.food_category_id == category_id,
                    FoodItemCategory.food_item_id == food_item_update.id
                ).first()
                if check_if_exist is None:
                    food_category = FoodItemCategory(
                        food_item_id=food_item_update.id,
                        food_category_id=category_id,
                        created_at=datetime.now(),
                    )
                    db.add(food_category)
                    db.commit()
        except Exception as e:
            db.rollback()
            error_msg = f"Error updating a food item category: {str(e)}"
            logger.exception(error_msg)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        try:
            for ingredient_id in item_request.food_ingredient_id:
                check_if_exist = db.query(FoodItemIngredient).filter(
                    FoodItemIngredient.food_ingredient_id == ingredient_id,
                    FoodItemIngredient.food_item_id == food_item_update.id
                ).first()
                if check_if_exist is None:
                    food_ingredient = FoodItemIngredient(
                        food_item_id=food_item_update.id,
                        food_ingredient_id=ingredient_id,
                        created_at=datetime.now(),
                    )
                    db.add(food_ingredient)
                    db.commit()
        except Exception as e:
            db.rollback()
            error_msg = f"Error updating a food item ingredient: {str(e)}"
            logger.exception(error_msg)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        try:
            for modifier_id in item_request.food_modifier_id:
                check_if_exist = db.query(FoodItemModifier).filter(
                    FoodItemModifier.food_modifier_id == modifier_id).first()
                if check_if_exist is None:
                    food_modifier = FoodItemModifier(
                        food_item_id=food_item_update.id,
                        food_modifier_id=modifier_id,
                        created_at=datetime.now(),
                    )
                    db.add(food_modifier)
                    db.commit()
        except Exception as e:
            db.rollback()
            error_msg = f"Error updating a food item modifier: {str(e)}"
            logger.exception(error_msg)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        return {"message": "Food Item updated successfully"}

    except Exception as e:
        db.rollback()
        error_msg = f"Error updating a food item: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/delete/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_food_item(id: int, db: db_dependency):
    food_item = db.query(FoodItems).filter(FoodItems.id == id).first()
    if food_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")
    try:
        db.query(FoodItemCategory).filter(FoodItemCategory.food_item_id == food_item.id).delete()
        db.query(FoodItemIngredient).filter(FoodItemIngredient.food_item_id == food_item.id).delete()
        db.query(FoodItemModifier).filter(FoodItemModifier.food_item_id == food_item.id).delete()

        # Delete the food item itself
        db.delete(food_item)
        db.commit()
    except Exception as e:
        db.rollback()
        error_msg = f"Error deleting a food item: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return {"message": "Food Item deleted successfully"}