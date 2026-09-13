from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(
    prefix="/api/categories",
    tags=["Категории"]
)

@router.post(
    "/",
    response_model=CategoryResponse,
)
def create_category(
        category: CategoryCreate,
        db: Session = Depends(get_db)
):
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
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
        db: Session = Depends(get_db)
    ):
    categories = db.query(Category).order_by(
        Category.sort_order,
        Category.id
        ).all()
    return categories

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )
    return category

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    category.name = category_data.name
    category.description = category_data.description
    category.parent_id = category_data.parent_id
    category.slug = category_data.slug
    category.image_url = category_data.image_url
    category.meta_title = category_data.meta_title
    category.meta_description = category_data.meta_description
    category.sort_order = category_data.sort_order
    category.is_active = category_data.is_active

    db.commit()
    db.refresh(category)
    return category

@router.delete(
    "/{category_id}",
    response_model=CategoryResponse,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    db.delete(category)
    db.commit()
    return { "message": "Категория успешно удалена", "category": category }