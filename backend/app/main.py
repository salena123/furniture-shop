from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import *
from app.routers.furniture_requests import router as furniture_requests_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router


app = FastAPI()
app.include_router(furniture_requests_router)
app.include_router(categories_router)
app.include_router(products_router)

@app.get("/")
def root():
    return {"message": "помидорка"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database": result.scalar()}