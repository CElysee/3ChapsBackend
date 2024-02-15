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
from models import FoodIngredients
from schemas import FoodItemCategoryCreate
from UploadFile import FileHandler

router = APIRouter(
    tags=["FoodIngredient"],
    prefix='/food_ingredient'
)

UPLOAD_FOLDER = "FoodIngredient"


def ingredient_by_id(category_id, db):
    category = db.query(FoodIngredients).filter(FoodIngredients.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient does not exist")
    return category


@router.get("/all")
async def get_food_ingredients(db: db_dependency):
    food_ingredient = db.query(FoodIngredients).all()
    return food_ingredient


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_food_ingredient(
        ingredient_name: str = Form(...),
        ingredient_status: str = Form(...),
        ingredient_description: str = Form(...),
        ingredient_image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Usage
    file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
    saved_filename = file_handler.save_uploaded_file(ingredient_image)
    # Check if Ingredient exist
    check_ingredient = db.query(FoodIngredients).filter(FoodIngredients.ingredient_name == ingredient_name).first()
    if check_ingredient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredient already exists")

    ingredient = FoodIngredients(
        ingredient_name=ingredient_name,
        ingredient_status=ingredient_status,
        ingredient_image=saved_filename,
        ingredient_description=ingredient_description,
        created_at=datetime.now(),
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return {"message": "Ingredient created successfully", "data": ingredient}


@router.get("/{ingredient_id}")
async def get_ingredient_by_id(ingredient: int, db: db_dependency):
    ingredient = ingredient_by_id(ingredient, db)
    return ingredient


@router.put("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_category(
        ingredient_id: int,
        ingredient_name: str = Form(None),
        ingredient_status: str = Form(None),
        ingredient_description: str = Form(None),
        ingredient_image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    ingredient = ingredient_by_id(ingredient_id, db)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient does not exist")
    try:

        if ingredient_name:
            ingredient.ingredient_name = ingredient_name
        if ingredient_status:
            ingredient.ingredient_status = ingredient_status
        if ingredient_image:
            file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)
            saved_filename = file_handler.save_uploaded_file(ingredient_image)
            ingredient.category_image = saved_filename
        if ingredient_description:
            ingredient.category_description = ingredient_description

        ingredient.updated_at = datetime.now()
        db.commit()
        return {"message": "Ingredient updated successfully"}

    except Exception as e:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return {"message": f"Error updating ingredient: {str(e)}"}


@router.delete("/delete", status_code=status.HTTP_202_ACCEPTED)
async def delete_ingredient(ingredient_id: int, db: db_dependency):
    ingredient = ingredient_by_id(ingredient_id, db)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient does not exist")
    db.delete(ingredient)
    db.commit()
    return {"message": "Ingredient deleted successfully"}
