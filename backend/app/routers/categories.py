from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.security import get_optional_current_user, require_admin

router = APIRouter(
    prefix="/api/categories",
    tags=["Категории"]
)


def _get_category_or_404(
    category_id: int,
    db: Session,
    include_inactive: bool = True
) -> Category:
    query = db.query(Category).filter(
        Category.id == category_id
    )

    if not include_inactive:
        query = query.filter(
            Category.is_active == True
        )

    category = query.first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    return category


def _ensure_category_slug_is_free(
    slug: str,
    db: Session,
    current_category_id: int | None = None
) -> None:
    existing_category = db.query(Category).filter(
        Category.slug == slug
    ).first()

    if existing_category and existing_category.id != current_category_id:
        raise HTTPException(
            status_code=400,
            detail="Категория с таким slug уже существует"
        )


def _commit_category_changes(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Не удалось сохранить категорию: проверьте slug и родителя"
        )


@router.post(
    "/",
    response_model=CategoryResponse,
)
def create_category(
        category: CategoryCreate,
        db: Session = Depends(get_db),
        _current_user: User = Depends(require_admin)
):
    _ensure_category_slug_is_free(category.slug, db)

    if category.parent_id is not None:
        _get_category_or_404(category.parent_id, db)

    new_category = Category(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        slug=category.slug,
        image_url=category.image_url,
        meta_title=category.meta_title,
        meta_description=category.meta_description,
        sort_order=category.sort_order,
        is_active=category.is_active
    )

    db.add(new_category)
    _commit_category_changes(db)
    db.refresh(new_category)
    return new_category

@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
    parent_id: int | None = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные категории может смотреть только администратор"
        )

    query = db.query(Category)

    if not include_inactive:
        query = query.filter(
            Category.is_active == True
        )

    if parent_id is not None:
        query = query.filter(
            Category.parent_id == parent_id
        )

    categories = query.order_by(
        Category.sort_order,
        Category.id
        ).all()
    return categories


@router.get(
    "/slug/{slug}",
    response_model=CategoryResponse,
)
def get_category_by_slug(
    slug: str,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные категории может смотреть только администратор"
        )

    query = db.query(Category).filter(
        Category.slug == slug
    )

    if not include_inactive:
        query = query.filter(
            Category.is_active == True
        )

    category = query.first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    return category

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные категории может смотреть только администратор"
        )

    return _get_category_or_404(
        category_id,
        db,
        include_inactive=include_inactive
    )

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    category = _get_category_or_404(category_id, db)
    _ensure_category_slug_is_free(
        category_data.slug,
        db,
        current_category_id=category.id
    )

    if category_data.parent_id == category.id:
        raise HTTPException(
            status_code=400,
            detail="Категория не может быть родителем самой себя"
        )

    if category_data.parent_id is not None:
        _get_category_or_404(category_data.parent_id, db)

    category.name = category_data.name
    category.description = category_data.description
    category.parent_id = category_data.parent_id
    category.slug = category_data.slug
    category.image_url = category_data.image_url
    category.meta_title = category_data.meta_title
    category.meta_description = category_data.meta_description
    category.sort_order = category_data.sort_order
    category.is_active = category_data.is_active

    _commit_category_changes(db)
    db.refresh(category)
    return category


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def patch_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    category = _get_category_or_404(category_id, db)
    update_data = category_data.model_dump(exclude_unset=True)

    for field in {"name", "slug", "sort_order", "is_active"}:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Поле {field} не может быть пустым"
            )

    if "slug" in update_data:
        _ensure_category_slug_is_free(
            update_data["slug"],
            db,
            current_category_id=category.id
        )

    if update_data.get("parent_id") == category.id:
        raise HTTPException(
            status_code=400,
            detail="Категория не может быть родителем самой себя"
        )

    if "parent_id" in update_data and update_data["parent_id"] is not None:
        _get_category_or_404(update_data["parent_id"], db)

    for field, value in update_data.items():
        setattr(category, field, value)

    _commit_category_changes(db)
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    category = _get_category_or_404(category_id, db)

    db.delete(category)
    db.commit()
    return { "message": "Категория успешно удалена"}
