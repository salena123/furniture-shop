import os
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
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
from app.routers.site_contacts import router as site_contacts_router
from app.routers.site_about import router as site_about_router
from app.settings import ALLOWED_ORIGINS, PRODUCTION, SESSION_COOKIE

app = FastAPI(docs_url=None if PRODUCTION else '/docs', redoc_url=None if PRODUCTION else '/redoc', openapi_url=None if PRODUCTION else '/openapi.json')


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
        "detail": [{"loc": item['loc'], "msg": item['msg'], "type": item['type']} for item in exc.errors()],
    }
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(content),
    )

@app.middleware('http')
async def browser_security(request: Request, call_next):
    if PRODUCTION and request.url.scheme != 'https':
        return JSONResponse(status_code=400, content={'message': 'Требуется HTTPS'})
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        origin = request.headers.get('origin')
        if origin is not None and origin not in ALLOWED_ORIGINS:
            return JSONResponse(status_code=403, content={'message': 'Недопустимый источник запроса'})
        cookie_auth = SESSION_COOKIE in request.cookies and not request.headers.get('authorization')
        if cookie_auth and request.headers.get('x-csrf-protection') != '1':
            return JSONResponse(status_code=403, content={'message': 'Не пройдена проверка защиты запроса'})
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    if PRODUCTION:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response

if PRODUCTION:
    allowed_hosts = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
    if not allowed_hosts or '*' in allowed_hosts:
        raise RuntimeError('Задайте ALLOWED_HOSTS для production')
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Protection"],
)

static_dir = Path(__file__).resolve().parents[1] / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard_router)
app.include_router(catalog_router)
app.include_router(site_contacts_router)
app.include_router(site_about_router)
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
