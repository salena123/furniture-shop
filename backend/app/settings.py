import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def validate_secret(value: str) -> str:
    if len(value.encode()) < 32 or any(word in value.lower() for word in ('change-me', 'dev-secret', 'replace-me', 'generate_random_secret')):
        raise RuntimeError('Задайте случайный SECRET_KEY длиной не менее 32 байт. Шаблонный ключ запрещён.')
    return value


TOKEN_SECRET = validate_secret(os.getenv('SECRET_KEY') or os.getenv('JWT_SECRET_KEY') or '')
PRODUCTION = os.getenv('APP_ENV', 'development') == 'production'
DATABASE_URL = os.getenv('DATABASE_URL', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
COOKIE_SECURE = PRODUCTION or os.getenv('COOKIE_SECURE', 'false').lower() == 'true'
SESSION_COOKIE = '__Host-furniture_session' if COOKIE_SECURE else 'furniture_session'
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',') if origin.strip()]
CSP_HEADER = os.getenv(
    'CONTENT_SECURITY_POLICY',
    "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
)
if '*' in ALLOWED_ORIGINS or (PRODUCTION and (not ALLOWED_ORIGINS or any(urlparse(origin).scheme != 'https' for origin in ALLOWED_ORIGINS))):
    raise RuntimeError('CORS_ORIGINS должен содержать точные адреса сайта; в production только HTTPS.')
if PRODUCTION and DATABASE_URL.startswith(('postgres://', 'postgresql://')) and 'sslmode=' not in DATABASE_URL:
    raise RuntimeError('В production DATABASE_URL PostgreSQL должен содержать sslmode=require или более строгий режим.')
if PRODUCTION and DATABASE_URL.startswith(('postgres://', 'postgresql://')) and 'sslmode=' not in DATABASE_URL:
    raise RuntimeError('В production DATABASE_URL PostgreSQL должен содержать sslmode=require или более строгий режим.')
