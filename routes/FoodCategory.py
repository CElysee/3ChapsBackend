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
from models import FoodCategories
from schemas import FoodItemCategoryCreate
from UploadFile import FileHandler

router = APIRouter(
    tags=["FoodCategory"],
    prefix='/food_category'
)

UPLOAD_FOLDER = "FoodCategory"


def category_by_id(category_id, db):
    category = db.query(FoodCategories).filter(FoodCategories.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")
    return category


@router.get("/all")
async def get_food_categories(db: db_dependency):
    food_category = db.query(FoodCategories).all()
    return food_category


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_food_category(
        category_name: str = Form(...),
        category_status: str = Form(...),
        category_description: str = Form(...),
        category_image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Usage
    file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
    saved_filename = file_handler.save_uploaded_file(category_image)
    # Check if Category exist
    check_category = db.query(FoodCategories).filter(FoodCategories.category_name == category_name).first()
    if check_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")

    category = FoodCategories(
        category_name=category_name,
        category_status=category_status,
        category_image=saved_filename,
        category_description=category_description,
        created_at=datetime.now(),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"message": "Category created successfully", "data": category}


@router.get("/{category_id}")
async def get_category_by_id(category_id: int, db: db_dependency):
    category = category_by_id(category_id, db)
    return category


@router.put("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_category(
        category_id: int,
        category_name: str = Form(None),
        category_status: str = Form(None),
        category_description: str = Form(None),
        category_image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    category = category_by_id(category_id, db)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")
    try:

        # Use the file_handler to save an uploaded file
        file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

        if category_name:
            category.category_name = category_name
        if category_status:
            category.category_status = category_status
        if category_image:
            saved_filename = file_handler.save_uploaded_file(category_image)
            category.category_image = saved_filename
        if category_description:
            category.category_description = category_description

        category.updated_at = datetime.now()
        db.commit()
        return {"message": "Category updated successfully"}

    except Exception as e:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return {"message": f"Error updating category: {str(e)}"}


@router.delete("/delete", status_code=status.HTTP_202_ACCEPTED)
async def delete_category(category_id: int, db: db_dependency):
    category = category_by_id(category_id, db)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
