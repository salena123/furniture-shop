import os
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
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


ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
}


def _get_error_message(detail) -> str:
    if isinstance(detail, str):
        return detail

    if isinstance(detail, dict):
        return str(detail.get("message") or detail.get("detail") or "Ошибка запроса")

    if isinstance(detail, list):
        return "Ошибка валидации данных"

    return "Ошибка запроса"


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
):
    content = {
        "error": ERROR_CODES.get(exc.status_code, "http_error"),
        "message": _get_error_message(exc.detail),
        "detail": exc.detail,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(content),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
):
    content = {
        "error": "validation_error",
        "message": "Ошибка валидации данных",
        "detail": exc.errors(),
    }
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(content),
    )

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
