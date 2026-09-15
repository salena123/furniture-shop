from pydantic import BaseModel
from datetime import datetime

class FurnitureCommentCreate(BaseModel):
    comment_text: str

class FurnitureCommentUpdate(BaseModel):
    comment_text: str

class FurnitureCommentResponse(BaseModel):
    id: int
    request_id: int
    user_id: int
    user_name: str | None = None
    user_role: str | None = None
    comment_text: str
    created_at: datetime

    class Config:
        from_attributes = True
