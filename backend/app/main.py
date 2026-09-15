import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import *
from app.routers.furniture_requests import router as furniture_requests_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.routers.attributes import router as attributes_router
from app.routers.product_attributes import router as product_attributes_router
from app.routers.furniture_comments import router as furniture_comments_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.dashboard import router as dashboard_router
from app.routers.materials import router as materials_router
from app.routers.catalog import router as catalog_router

app = FastAPI()

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:5173,http://127.0.0.1:5173"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parents[1] / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard_router)
app.include_router(catalog_router)
app.include_router(furniture_requests_router)
app.include_router(categories_router)
app.include_router(materials_router)
app.include_router(products_router)
app.include_router(attributes_router)
app.include_router(product_attributes_router)
app.include_router(furniture_comments_router)


@app.get("/")
def root():
    return {"message": "помидорка"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database": result.scalar()}
