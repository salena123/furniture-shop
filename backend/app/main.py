from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import *
from app.routers.furniture_requests import router as furniture_requests_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.routers.attributes import router as attributes_router
from app.routers.product_attributes import router as product_attributes_router
from app.routers.furniture_comments import router as furniture_comments_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(furniture_requests_router)
app.include_router(categories_router)
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
