from datetime import datetime

from pydantic import BaseModel, ConfigDict

class FurnitureCommentCreate(BaseModel):
    comment_text: str

class FurnitureCommentUpdate(BaseModel):
    comment_text: str

class FurnitureCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    user_id: int
    user_name: str | None = None
    user_role: str | None = None
    comment_text: str
    created_at: datetime
