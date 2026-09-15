import os

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.attribute import Attribute
from app.models.attribute_value import AttributeValue
from app.models.category import Category
from app.models.furniture_comment import FurnitureComment
from app.models.furniture_request import FurnitureRequest
from app.models.material import Material
from app.models.product import Product
from app.models.product_attribute import ProductAttribute
from app.models.request_event import RequestEvent
from app.models.user import User
from app.security import hash_password


ADMIN_LOGIN = os.getenv("SEED_ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin12345")
ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Администратор")
MANAGER_LOGIN = os.getenv("SEED_MANAGER_LOGIN", "manager")
MANAGER_PASSWORD = os.getenv("SEED_MANAGER_PASSWORD", "manager12345")
MANAGER_NAME = os.getenv("SEED_MANAGER_NAME", "Менеджер")


def _get_or_create(db: Session, model, defaults: dict | None = None, **lookup):
    item = db.query(model).filter_by(**lookup).first()
    if item:
        return item, False

    item = model(**lookup, **(defaults or {}))
    db.add(item)
    db.flush()

    return item, True


def _get_materials_by_name(db: Session) -> dict[str, Material]:
    return {
        material.name: material
        for material in db.query(Material).all()
    }


def _get_categories_by_slug(db: Session) -> dict[str, Category]:
    return {
        category.slug: category
        for category in db.query(Category).all()
    }


def _get_attribute_values(db: Session) -> dict[tuple[str, str], AttributeValue]:
    values = db.query(AttributeValue).join(Attribute).all()

    return {
        (value.attribute.name, value.value): value
        for value in values
    }


def _create_users(db: Session) -> dict[str, int]:
    summary = {"users": 0}

    _, created = _get_or_create(
        db,
        User,
        login=ADMIN_LOGIN,
        defaults={
            "name": ADMIN_NAME,
            "email": os.getenv("SEED_ADMIN_EMAIL"),
            "password_hash": hash_password(ADMIN_PASSWORD),
            "role": "admin",
        }
    )
    summary["users"] += int(created)

    _, created = _get_or_create(
        db,
        User,
        login=MANAGER_LOGIN,
        defaults={
            "name": MANAGER_NAME,
            "email": os.getenv("SEED_MANAGER_EMAIL"),
            "password_hash": hash_password(MANAGER_PASSWORD),
            "role": "manager",
        }
    )
    summary["users"] += int(created)

    return summary


def _create_categories(db: Session) -> dict[str, int]:
    summary = {"categories": 0}
    category_specs = [
        {
            "name": "Кухни",
            "slug": "kuhni",
            "description": "Кухонные гарнитуры по размерам помещения",
            "sort_order": 10,
        },
        {
            "name": "Шкафы",
            "slug": "shkafy",
            "description": "Распашные шкафы и шкафы-купе",
            "sort_order": 20,
        },
        {
            "name": "Комоды",
            "slug": "komody",
            "description": "Комоды для спальни, прихожей и гостиной",
            "sort_order": 30,
        },
        {
            "name": "Прихожие",
            "slug": "prihozhie",
            "description": "Мебель для входной зоны",
            "sort_order": 40,
        },
    ]

    for spec in category_specs:
        _, created = _get_or_create(
            db,
            Category,
            slug=spec["slug"],
            defaults={
                "name": spec["name"],
                "description": spec["description"],
                "sort_order": spec["sort_order"],
                "is_active": True,
            }
        )
        summary["categories"] += int(created)

    return summary


def _create_materials(db: Session) -> dict[str, int]:
    summary = {"materials": 0}
    material_specs = [
        {
            "name": "ЛДСП",
            "description": "Практичный плитный материал для корпусной мебели",
        },
        {
            "name": "МДФ",
            "description": "Плотный материал для фасадов и декоративных элементов",
        },
        {
            "name": "Массив дерева",
            "description": "Натуральная древесина для премиальной мебели",
        },
        {
            "name": "Шпон",
            "description": "Тонкий слой натурального дерева на устойчивой основе",
        },
    ]

    for spec in material_specs:
        _, created = _get_or_create(
            db,
            Material,
            name=spec["name"],
            defaults={
                "description": spec["description"],
            }
        )
        summary["materials"] += int(created)

    return summary


def _create_attributes(db: Session) -> dict[str, int]:
    summary = {"attributes": 0, "attribute_values": 0}
    attribute_specs = {
        "Цвет": ["Белый", "Графит", "Дуб сонома", "Венге"],
        "Стиль": ["Современный", "Классика", "Минимализм"],
        "Тип изделия": ["Корпусная мебель", "Мебель на заказ"],
    }

    for attribute_name, values in attribute_specs.items():
        attribute, created = _get_or_create(
            db,
            Attribute,
            name=attribute_name,
            defaults={"is_active": True}
        )
        summary["attributes"] += int(created)

        for sort_order, value in enumerate(values, start=10):
            _, created = _get_or_create(
                db,
                AttributeValue,
                attribute_id=attribute.id,
                value=value,
                defaults={"sort_order": sort_order}
            )
            summary["attribute_values"] += int(created)

    return summary


def _create_products(db: Session) -> dict[str, int]:
    summary = {"products": 0, "product_attributes": 0}
    categories = _get_categories_by_slug(db)
    materials = _get_materials_by_name(db)
    attribute_values = _get_attribute_values(db)
    product_specs = [
        {
            "product_name": "Кухня Практика",
            "slug": "kuhnya-praktika",
            "category_slug": "kuhni",
            "material_name": "МДФ",
            "price": "от 85 000 ₽",
            "short_description": "Лаконичный гарнитур для прямой или угловой кухни",
            "description": "Подходит для квартир и частных домов, размеры рассчитываются индивидуально.",
            "article": "KM-001",
            "is_custom": True,
            "sort_order": 10,
            "dimensions": "по размерам заказчика",
            "color": "Белый / Дуб сонома",
            "attributes": [("Цвет", "Белый"), ("Стиль", "Современный"), ("Тип изделия", "Мебель на заказ")],
        },
        {
            "product_name": "Шкаф Купе Линия",
            "slug": "shkaf-kupe-liniya",
            "category_slug": "shkafy",
            "material_name": "ЛДСП",
            "price": "от 48 000 ₽",
            "short_description": "Вместительный шкаф-купе с раздвижными дверями",
            "description": "Можно подобрать наполнение, фасады и цвет корпуса.",
            "article": "SH-014",
            "is_custom": True,
            "sort_order": 20,
            "dimensions": "1800 x 600 x 2400 мм",
            "color": "Графит",
            "attributes": [("Цвет", "Графит"), ("Стиль", "Минимализм"), ("Тип изделия", "Корпусная мебель")],
        },
        {
            "product_name": "Комод Норд",
            "slug": "komod-nord",
            "category_slug": "komody",
            "material_name": "Шпон",
            "price": "от 32 000 ₽",
            "short_description": "Комод с мягкой древесной фактурой",
            "description": "Подходит для спальни, гостиной или прихожей.",
            "article": "KD-008",
            "is_custom": False,
            "sort_order": 30,
            "dimensions": "900 x 450 x 850 мм",
            "color": "Венге",
            "attributes": [("Цвет", "Венге"), ("Стиль", "Классика"), ("Тип изделия", "Корпусная мебель")],
        },
    ]

    for spec in product_specs:
        material = materials[spec["material_name"]]
        product, created = _get_or_create(
            db,
            Product,
            slug=spec["slug"],
            defaults={
                "product_name": spec["product_name"],
                "description": spec["description"],
                "short_description": spec["short_description"],
                "article": spec["article"],
                "category_id": categories[spec["category_slug"]].id,
                "material_id": material.id,
                "price": spec["price"],
                "material": material.name,
                "is_custom": spec["is_custom"],
                "is_active": True,
                "sort_order": spec["sort_order"],
                "dimensions": spec["dimensions"],
                "color": spec["color"],
                "meta_title": spec["product_name"],
                "meta_description": spec["short_description"],
            }
        )
        summary["products"] += int(created)

        for attribute_key in spec["attributes"]:
            value = attribute_values[attribute_key]
            _, created = _get_or_create(
                db,
                ProductAttribute,
                product_id=product.id,
                attribute_value_id=value.id,
            )
            summary["product_attributes"] += int(created)

    return summary


def _create_requests(db: Session) -> dict[str, int]:
    summary = {"requests": 0, "comments": 0, "events": 0}
    manager = db.query(User).filter_by(login=MANAGER_LOGIN).first()
    products = {
        product.slug: product
        for product in db.query(Product).all()
    }
    request_specs = [
        {
            "client_name": "Анна Смирнова",
            "phone": "+7 900 100-20-30",
            "product_slug": "kuhnya-praktika",
            "color_name": "Белый / Дуб сонома",
            "needs_measurements": True,
            "dimensions": "кухня 3200 мм",
            "comment": "Нужна консультация по угловой кухне",
            "status": "new",
            "assigned_manager_id": None,
        },
        {
            "client_name": "Игорь Волков",
            "phone": "+7 900 200-30-40",
            "product_slug": "shkaf-kupe-liniya",
            "color_name": "Графит",
            "needs_measurements": False,
            "dimensions": "1800 x 600 x 2400 мм",
            "comment": "Просит перезвонить вечером",
            "status": "in_progress",
            "assigned_manager_id": manager.id if manager else None,
        },
    ]

    for spec in request_specs:
        product = products[spec["product_slug"]]
        existing_request = db.query(FurnitureRequest).filter_by(
            client_name=spec["client_name"],
            phone=spec["phone"],
            product_name=product.product_name,
        ).first()

        if existing_request:
            request = existing_request
        else:
            request = FurnitureRequest(
                product_id=product.id,
                material_id=product.material_id,
                product_name=product.product_name,
                color_name=spec["color_name"],
                needs_measurements=spec["needs_measurements"],
                dimensions=spec["dimensions"],
                client_name=spec["client_name"],
                phone=spec["phone"],
                status=spec["status"],
                assigned_manager_id=spec["assigned_manager_id"],
                comment=spec["comment"],
            )
            db.add(request)
            db.flush()
            summary["requests"] += 1

        if request.status == "in_progress" and manager:
            _, created = _get_or_create(
                db,
                RequestEvent,
                request_id=request.id,
                user_id=manager.id,
                event_type="status_changed",
                old_status="new",
                new_status="in_progress",
                defaults={
                    "message": "Менеджер взял заявку в работу",
                }
            )
            summary["events"] += int(created)

            _, created = _get_or_create(
                db,
                FurnitureComment,
                request_id=request.id,
                user_id=manager.id,
                comment_text="Клиент просит перезвонить после 18:00",
            )
            summary["comments"] += int(created)

    return summary


def seed_database() -> dict[str, int]:
    db = SessionLocal()
    summary = {
        "users": 0,
        "categories": 0,
        "materials": 0,
        "attributes": 0,
        "attribute_values": 0,
        "products": 0,
        "product_attributes": 0,
        "requests": 0,
        "comments": 0,
        "events": 0,
    }

    try:
        for part in (
            _create_users(db),
            _create_categories(db),
            _create_materials(db),
            _create_attributes(db),
            _create_products(db),
            _create_requests(db),
        ):
            for key, value in part.items():
                summary[key] += value

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return summary


def main() -> None:
    summary = seed_database()

    print("Seed completed")
    for name, count in summary.items():
        print(f"{name}: {count}")
    print(f"admin login: {ADMIN_LOGIN}")
    print(f"admin password: {ADMIN_PASSWORD}")
    print(f"manager login: {MANAGER_LOGIN}")
    print(f"manager password: {MANAGER_PASSWORD}")


if __name__ == "__main__":
    main()
