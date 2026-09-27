from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category


def visible_category_ids(db: Session) -> set[int]:
    children = defaultdict(list)
    for category in db.query(Category.id, Category.parent_id, Category.is_active):
        if category.is_active:
            children[category.parent_id].append(category.id)
    visible = set()
    pending = list(children[None])
    while pending:
        category_id = pending.pop()
        if category_id not in visible:
            visible.add(category_id)
            pending.extend(children[category_id])
    return visible


def descendant_category_ids(category_id: int, db: Session) -> set[int]:
    children = defaultdict(list)
    for row in db.query(Category.id, Category.parent_id):
        children[row.parent_id].append(row.id)
    descendants = set()
    pending = [category_id]
    while pending:
        current_id = pending.pop()
        if current_id not in descendants:
            descendants.add(current_id)
            pending.extend(children[current_id])
    return descendants


def validate_category_parent(category_id: int, parent_id: int | None, db: Session) -> None:
    if parent_id in descendant_category_ids(category_id, db):
        raise HTTPException(
            status_code=400,
            detail="Нельзя переместить категорию в саму себя или в её подкатегорию",
        )
