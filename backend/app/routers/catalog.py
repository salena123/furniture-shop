from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.attribute import Attribute
from app.models.category import Category
from app.models.material import Material
from app.schemas.catalog import CatalogOptionsResponse


router = APIRouter(
    prefix="/api/catalog",
    tags=["Каталог"]
)


@router.get(
    "/options",
    response_model=CatalogOptionsResponse
)
def get_catalog_options(
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter(
        Category.is_active == True
    ).order_by(
        Category.sort_order,
        Category.id
    ).all()

    materials = db.query(Material).order_by(
        Material.name,
        Material.id
    ).all()

    attributes = db.query(Attribute).options(
        selectinload(Attribute.values)
    ).filter(
        Attribute.is_active == True
    ).order_by(
        Attribute.id
    ).all()

    for attribute in attributes:
        attribute.values.sort(
            key=lambda value: (value.sort_order, value.id)
        )

    return {
        "categories": categories,
        "materials": materials,
        "attributes": attributes,
    }
