import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContactsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=500)
    hours: str | None = Field(default=None, max_length=300)
    email: str | None = Field(default=None, max_length=254)

    @field_validator("phone", "address", "hours", "email", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value and (not re.fullmatch(r"\+?[0-9 ()-]+", value) or not 7 <= len(re.sub(r"\D", "", value)) <= 20):
            raise ValueError("Укажите телефон: от 7 до 20 цифр, допустимы +, пробелы, скобки и дефисы")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Укажите корректный адрес электронной почты")
        return value


class ContactsResponse(ContactsUpdate):
    model_config = ConfigDict(from_attributes=True)
    configured: bool = False
