from pydantic import BaseModel
from datetime import datetime

class FurnitureCommentCreate(BaseModel):
    comment_text: str

class FurnitureCommentResponse(BaseModel):
    id: int
    request_id: int
    user_id: int
    comment_text: str
    created_at: datetime

    class Config:
        from_attributes = True