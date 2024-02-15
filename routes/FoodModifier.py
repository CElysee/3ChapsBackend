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
from models import FoodModifiers
from UploadFile import FileHandler

router = APIRouter(
    tags=["FoodModifier"],
    prefix='/food_modifier'
)

UPLOAD_FOLDER = "FoodModifier"


def modifier_by_id(modifier_id, db):
    modifier = db.query(FoodModifiers).filter(FoodModifiers.id == modifier_id).first()
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food modifier does not exist")
    return modifier


@router.get("/all")
async def get_food_modifiers(db: db_dependency):
    food_modifier = db.query(FoodModifiers).all()
    return food_modifier


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_food_modifier(
        modifier_name: str = Form(...),
        modifier_description: str = Form(...),
        modifier_image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Usage
    file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)

    # Use the file_handler to save an uploaded file
    saved_filename = file_handler.save_uploaded_file(modifier_image)
    # Check if modifier exist
    check_modifier = db.query(FoodModifiers).filter(FoodModifiers.modifier_name == modifier_name).first()
    if check_modifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="modifier already exists")

    modifier = FoodModifiers(
        modifier_name=modifier_name,
        modifier_image=saved_filename,
        modifier_description=modifier_description,
        created_at=datetime.now(),
    )
    db.add(modifier)
    db.commit()
    db.refresh(modifier)
    return {"message": "Food Modifier created successfully", "data": modifier}


@router.get("/{modifier_id}")
async def get_modifier_by_id(modifier: int, db: db_dependency):
    modifier = modifier_by_id(modifier, db)
    return modifier


@router.put("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_category(
        modifier_id: int,
        modifier_name: str = Form(None),
        modifier_description: str = Form(None),
        modifier_image: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    modifier = modifier_by_id(modifier_id, db)
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food modifier does not exist")
    try:

        if modifier_name:
            modifier.modifier_name = modifier_name
        if modifier_image:
            file_handler = FileHandler(upload_folder=UPLOAD_FOLDER)
            saved_filename = file_handler.save_uploaded_file(modifier_image)
            modifier.modifier_image = saved_filename
        if modifier_description:
            modifier.category_description = modifier_description

        modifier.updated_at = datetime.now()
        db.commit()
        return {"message": "modifier updated successfully"}

    except Exception as e:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return {"message": f"Error updating modifier: {str(e)}"}


@router.delete("/delete", status_code=status.HTTP_202_ACCEPTED)
async def delete_modifier(modifier_id: int, db: db_dependency):
    modifier = modifier_by_id(modifier_id, db)
    if not modifier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food modifier does not exist")
    db.delete(modifier)
    db.commit()
    return {"message": "modifier deleted successfully"}
