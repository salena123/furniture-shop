from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.validators import normalize_required_text

class FurnitureCommentCreate(BaseModel):
    comment_text: str

    @field_validator("comment_text", mode="before")
    @classmethod
    def validate_comment_text_field(cls, value):
        return normalize_required_text(value, "comment_text")

class FurnitureCommentUpdate(BaseModel):
    comment_text: str

    @field_validator("comment_text", mode="before")
    @classmethod
    def validate_comment_text_field(cls, value):
        return normalize_required_text(value, "comment_text")

class FurnitureCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    user_id: int
    user_name: str | None = None
    user_role: str | None = None
    comment_text: str
    created_at: datetime
