from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

UserRole = Literal["admin", "manager"]

class UserCreate(BaseModel):
    login: str
    name: str
    email: str | None = None
    password: str
    role: UserRole = "manager"

class UserUpdate(BaseModel):
    login: str | None = None
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: UserRole | None = None

class UserLogin(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    name: str
    email: str | None  
    role: str
    last_login_at: datetime | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: datetime
    user: UserResponse
