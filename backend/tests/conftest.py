import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DB_PATH = Path(tempfile.gettempdir()) / "furniture_shop_api_tests.sqlite"

sys.path.insert(0, str(BACKEND_DIR))

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "test-only-secret-57f298413ab74f3bb3fc9d8e9"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ['APP_ENV'] = 'development'
os.environ['COOKIE_SECURE'] = 'false'
os.environ['CORS_ORIGINS'] = 'http://localhost:3000,http://127.0.0.1:3000'

from app import models  # noqa: E402,F401
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def remove_test_database_file():
    yield
    engine.dispose()
    TEST_DB_PATH.unlink(missing_ok=True)
