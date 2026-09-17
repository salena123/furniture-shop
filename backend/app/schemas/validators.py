import re
from typing import Any


LOGIN_RE = re.compile(r"^[A-Za-z0-9_.-]{3,100}$")
PHONE_RE = re.compile(r"^\+?[0-9\s().-]{7,25}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def normalize_optional_text(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value or None

    return value


def normalize_required_text(value: Any, field_name: str = "Поле") -> Any:
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValueError(f"{field_name} не может быть пустым")
        return value

    if value is None:
        raise ValueError(f"{field_name} не может быть пустым")

    return value


def validate_login(value: Any) -> Any:
    value = normalize_required_text(value, "login")

    if isinstance(value, str) and not LOGIN_RE.fullmatch(value):
        raise ValueError(
            "login должен быть от 3 символов и содержать только латиницу, цифры, точку, дефис или подчёркивание"
        )

    return value


def validate_password(value: Any) -> Any:
    value = normalize_required_text(value, "password")

    if isinstance(value, str) and len(value) < 8:
        raise ValueError("password должен быть не короче 8 символов")

    return value


def validate_phone(value: Any) -> Any:
    value = normalize_required_text(value, "phone")

    if isinstance(value, str) and not PHONE_RE.fullmatch(value):
        raise ValueError("phone должен быть похож на номер телефона")

    return value


def validate_slug(value: Any) -> Any:
    value = normalize_required_text(value, "slug")

    if isinstance(value, str) and not SLUG_RE.fullmatch(value):
        raise ValueError(
            "slug должен содержать только маленькие латинские буквы, цифры и дефисы"
        )

    return value


def validate_true(value: Any, field_name: str) -> Any:
    if value is not True:
        raise ValueError(f"{field_name} должно быть принято")

    return value
