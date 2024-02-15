from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from fastapi.staticfiles import StaticFiles
import os
from cachetools import TTLCache
import models
from database import engine, db_dependency
from routes import (auth)
from routes.auth import get_current_user, user_dependency

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
