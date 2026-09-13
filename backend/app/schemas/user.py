from pydantic import BaseModel

class UserCreate(BaseModel):
    login: str
    name: str
    email: str | None = None
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    login: str
    name: str
    email: str | None  
    role: str

    class Config:
        from_attributes = True