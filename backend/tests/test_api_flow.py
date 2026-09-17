from datetime import datetime, timedelta, timezone

import jwt

from app.models.user import User
from app.security import JWT_ALGORITHM, TOKEN_SECRET, create_access_token


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def _create_admin(client) -> dict:
    response = client.post(
        "/api/users/bootstrap-admin",
        json={
            "login": "admin",
            "name": "Admin",
            "email": "admin@example.com",
            "password": "admin12345",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    return response.json()


def _login(client, login: str, password: str) -> dict:
    response = client.post(
        "/api/auth/login",
        json={
            "login": login,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()


def _create_manager(
    client,
    admin_token: str,
    login: str = "manager",
    name: str = "Manager",
    password: str = "manager12345",
) -> dict:
    response = client.post(
        "/api/users/",
        headers=_auth_headers(admin_token),
        json={
            "login": login,
            "name": name,
            "email": f"{login}@example.com",
            "password": password,
            "role": "manager",
        },
    )

    assert response.status_code == 201
    return response.json()


def _create_category(client, admin_token: str, slug: str = "kuhni") -> dict:
    response = client.post(
        "/api/categories/",
        headers=_auth_headers(admin_token),
        json={
            "name": "Кухни",
            "description": "Кухонные гарнитуры",
            "slug": slug,
            "sort_order": 10,
            "is_active": True,
        },
    )

    assert response.status_code == 200
    return response.json()


def _create_material(client, admin_token: str, name: str = "МДФ") -> dict:
    response = client.post(
        "/api/materials/",
        headers=_auth_headers(admin_token),
        json={
            "name": name,
            "description": "Материал для фасадов",
        },
    )

    assert response.status_code == 200
    return response.json()


def _create_product(
    client,
    admin_token: str,
    category_id: int,
    material_id: int,
    slug: str = "kuhnya-test",
) -> dict:
    response = client.post(
        "/api/products/",
        headers=_auth_headers(admin_token),
        json={
            "product_name": "Кухня Тест",
            "slug": slug,
            "description": "Тестовый товар",
            "short_description": "Короткое описание",
            "article": "TEST-1",
            "category_id": category_id,
            "material_id": material_id,
            "price": "от 50 000 ₽",
            "material": "МДФ",
            "is_custom": True,
            "is_active": True,
            "sort_order": 10,
            "dimensions": "по размерам заказчика",
            "color": "Белый",
        },
    )

    assert response.status_code == 200
    return response.json()


def _create_public_request(client, product: dict, material: dict) -> dict:
    response = client.post(
        "/api/requests/",
        json={
            "product_id": product["id"],
            "material_id": material["id"],
            "needs_measurements": True,
            "dimensions": "3000 мм",
            "client_name": "Анна",
            "phone": "+7 900 100-20-30",
            "city": "Екатеринбург",
            "preferred_contact_time": "после 14:00",
            "personal_data_consent": True,
            "comment": "Перезвонить после обеда",
        },
    )

    assert response.status_code == 200
    return response.json()


def _create_attribute(client, admin_token: str) -> dict:
    response = client.post(
        "/api/attributes/",
        headers=_auth_headers(admin_token),
        json={
            "name": "Цвет",
            "is_active": True,
        },
    )

    assert response.status_code == 200
    return response.json()


def _create_attribute_value(client, admin_token: str, attribute_id: int) -> dict:
    response = client.post(
        f"/api/attributes/{attribute_id}/values",
        headers=_auth_headers(admin_token),
        json={
            "value": "Белый",
            "sort_order": 10,
        },
    )

    assert response.status_code == 200
    return response.json()


def test_login_returns_token_expiration_and_me_uses_bearer(client):
    _create_admin(client)

    token_response = _login(client, "admin", "admin12345")

    assert token_response["token_type"] == "bearer"
    assert token_response["access_token"]
    assert token_response["access_token"].count(".") == 2
    assert 0 < token_response["expires_in"] <= 3600
    assert datetime.fromisoformat(token_response["expires_at"]) > datetime.now(timezone.utc)

    payload = jwt.decode(
        token_response["access_token"],
        TOKEN_SECRET,
        algorithms=[JWT_ALGORITHM],
    )
    assert payload["type"] == "access"
    assert payload["role"] == "admin"

    me_response = client.get(
        "/api/auth/me",
        headers=_auth_headers(token_response["access_token"]),
    )

    assert me_response.status_code == 200
    assert me_response.json()["login"] == "admin"


def test_expired_token_is_rejected(client, db_session):
    _create_admin(client)
    user = db_session.query(User).filter_by(login="admin").first()
    expired_token = create_access_token(
        user,
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    response = client.get(
        "/api/auth/me",
        headers=_auth_headers(expired_token),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_manager_cannot_create_product(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    _create_manager(client, admin_token)
    manager_token = _login(client, "manager", "manager12345")["access_token"]
    category = _create_category(client, admin_token)
    material = _create_material(client, admin_token)

    response = client.post(
        "/api/products/",
        headers=_auth_headers(manager_token),
        json={
            "product_name": "Шкаф",
            "slug": "shkaf-test",
            "category_id": category["id"],
            "material_id": material["id"],
            "price": "от 40 000 ₽",
            "is_custom": True,
        },
    )

    assert response.status_code == 403


def test_public_request_and_manager_processing_flow(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    manager = _create_manager(client, admin_token)
    manager_token = _login(client, "manager", "manager12345")["access_token"]
    category = _create_category(client, admin_token)
    material = _create_material(client, admin_token)
    product = _create_product(client, admin_token, category["id"], material["id"])

    request = _create_public_request(client, product, material)
    assert request["status"] == "new"
    assert request["product_name"] == product["product_name"]
    assert request["color_name"] == product["color"]
    assert request["material_name"] == material["name"]
    assert request["city"] == "Екатеринбург"
    assert request["personal_data_consent"] is True

    unauthorized_response = client.get("/api/requests/")
    assert unauthorized_response.status_code == 401

    take_response = client.patch(
        f"/api/requests/{request['id']}/take",
        headers=_auth_headers(manager_token),
    )
    assert take_response.status_code == 200
    assert take_response.json()["assigned_manager_id"] == manager["id"]

    status_response = client.patch(
        f"/api/requests/{request['id']}/status",
        headers=_auth_headers(manager_token),
        json={"status": "contacted"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "contacted"

    comment_response = client.post(
        f"/api/requests/{request['id']}/comments",
        headers=_auth_headers(manager_token),
        json={"comment_text": "Клиент ждёт расчёт"},
    )
    assert comment_response.status_code == 200
    assert comment_response.json()["user_role"] == "manager"

    list_response = client.get(
        "/api/requests/?limit=10&offset=0",
        headers=_auth_headers(manager_token),
    )
    list_payload = list_response.json()

    assert list_response.status_code == 200
    assert list_payload["total"] == 1
    assert list_payload["limit"] == 10
    assert list_payload["offset"] == 0
    assert len(list_payload["items"]) == 1
    assert list_payload["items"][0]["comments_count"] == 1
    assert list_payload["items"][0]["events_count"] == 3
    assert list_payload["items"][0]["product_slug"] == product["slug"]
    assert list_payload["items"][0]["category_name"] == category["name"]


def test_catalog_lists_return_pagination_meta(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    category = _create_category(client, admin_token)
    first_material = _create_material(client, admin_token, "МДФ")
    second_material = _create_material(client, admin_token, "ЛДСП")
    _create_product(client, admin_token, category["id"], first_material["id"], "kuhnya-first")
    _create_product(client, admin_token, category["id"], second_material["id"], "kuhnya-second")

    products_response = client.get("/api/products/?limit=1&offset=1")
    products_payload = products_response.json()

    assert products_response.status_code == 200
    assert products_payload["total"] == 2
    assert products_payload["limit"] == 1
    assert products_payload["offset"] == 1
    assert len(products_payload["items"]) == 1

    materials_response = client.get("/api/materials/?limit=1&offset=0")
    materials_payload = materials_response.json()

    assert materials_response.status_code == 200
    assert materials_payload["total"] == 2
    assert materials_payload["limit"] == 1
    assert materials_payload["offset"] == 0
    assert len(materials_payload["items"]) == 1


def test_validation_rejects_invalid_payloads(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    category = _create_category(client, admin_token)
    material = _create_material(client, admin_token)

    invalid_phone_response = client.post(
        "/api/requests/",
        json={
            "product_name": "Кухня",
            "needs_measurements": True,
            "client_name": "Анна",
            "phone": "not-a-phone",
        },
    )
    assert invalid_phone_response.status_code == 422

    blank_material_response = client.post(
        "/api/materials/",
        headers=_auth_headers(admin_token),
        json={
            "name": "   ",
            "description": "Описание",
        },
    )
    assert blank_material_response.status_code == 422

    invalid_slug_response = client.post(
        "/api/products/",
        headers=_auth_headers(admin_token),
        json={
            "product_name": "Кухня",
            "slug": "bad slug",
            "category_id": category["id"],
            "material_id": material["id"],
            "price": "от 50 000 ₽",
            "is_custom": True,
        },
    )
    assert invalid_slug_response.status_code == 422

    missing_product_response = client.post(
        "/api/requests/",
        json={
            "needs_measurements": True,
            "client_name": "Анна",
            "phone": "+7 900 100-20-30",
            "personal_data_consent": True,
        },
    )
    assert missing_product_response.status_code == 422


def test_safe_deletion_preserves_request_history(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    category = _create_category(client, admin_token)
    material = _create_material(client, admin_token)
    product = _create_product(client, admin_token, category["id"], material["id"])
    request = _create_public_request(client, product, material)

    category_delete_response = client.delete(
        f"/api/categories/{category['id']}",
        headers=_auth_headers(admin_token),
    )
    assert category_delete_response.status_code == 400

    material_delete_response = client.delete(
        f"/api/materials/{material['id']}",
        headers=_auth_headers(admin_token),
    )
    assert material_delete_response.status_code == 200
    assert material_delete_response.json()["updated_products"] == 1
    assert material_delete_response.json()["updated_requests"] == 1

    product_delete_response = client.delete(
        f"/api/products/{product['id']}",
        headers=_auth_headers(admin_token),
    )
    assert product_delete_response.status_code == 200
    assert product_delete_response.json()["is_active"] is False

    request_response = client.get(
        f"/api/requests/{request['id']}",
        headers=_auth_headers(admin_token),
    )
    request_payload = request_response.json()

    assert request_response.status_code == 200
    assert request_payload["product_id"] == product["id"]
    assert request_payload["material_id"] is None
    assert request_payload["product_name"] == product["product_name"]


def test_attribute_delete_is_blocked_while_used_by_product(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    category = _create_category(client, admin_token)
    material = _create_material(client, admin_token)
    product = _create_product(client, admin_token, category["id"], material["id"])
    attribute = _create_attribute(client, admin_token)
    value = _create_attribute_value(client, admin_token, attribute["id"])

    link_response = client.post(
        f"/api/products/{product['id']}/attributes/{value['id']}",
        headers=_auth_headers(admin_token),
    )
    assert link_response.status_code == 200

    value_delete_response = client.delete(
        f"/api/attributes/values/{value['id']}",
        headers=_auth_headers(admin_token),
    )
    assert value_delete_response.status_code == 400

    attribute_delete_response = client.delete(
        f"/api/attributes/{attribute['id']}",
        headers=_auth_headers(admin_token),
    )
    assert attribute_delete_response.status_code == 400

    unlink_response = client.delete(
        f"/api/products/{product['id']}/attributes/{value['id']}",
        headers=_auth_headers(admin_token),
    )
    assert unlink_response.status_code == 200

    value_delete_response = client.delete(
        f"/api/attributes/values/{value['id']}",
        headers=_auth_headers(admin_token),
    )
    assert value_delete_response.status_code == 200

    attribute_delete_response = client.delete(
        f"/api/attributes/{attribute['id']}",
        headers=_auth_headers(admin_token),
    )
    assert attribute_delete_response.status_code == 200


def test_user_delete_detaches_requests_but_blocks_history_authors(client):
    _create_admin(client)
    admin_token = _login(client, "admin", "admin12345")["access_token"]
    manager = _create_manager(client, admin_token)
    second_manager = _create_manager(
        client,
        admin_token,
        login="manager2",
        name="Second Manager",
        password="manager2345",
    )
    second_manager_token = _login(client, "manager2", "manager2345")["access_token"]
    category = _create_category(client, admin_token)
    material = _create_material(client, admin_token)
    product = _create_product(client, admin_token, category["id"], material["id"])
    request = _create_public_request(client, product, material)

    assign_response = client.patch(
        f"/api/requests/{request['id']}/manager",
        headers=_auth_headers(admin_token),
        json={"assigned_manager_id": manager["id"]},
    )
    assert assign_response.status_code == 200

    delete_manager_response = client.delete(
        f"/api/users/{manager['id']}",
        headers=_auth_headers(admin_token),
    )
    assert delete_manager_response.status_code == 200
    assert delete_manager_response.json()["detached_requests"] == 1

    request_response = client.get(
        f"/api/requests/{request['id']}",
        headers=_auth_headers(admin_token),
    )
    assert request_response.json()["assigned_manager_id"] is None

    comment_response = client.post(
        f"/api/requests/{request['id']}/comments",
        headers=_auth_headers(second_manager_token),
        json={"comment_text": "Перезвонить завтра"},
    )
    assert comment_response.status_code == 200

    delete_second_manager_response = client.delete(
        f"/api/users/{second_manager['id']}",
        headers=_auth_headers(admin_token),
    )
    assert delete_second_manager_response.status_code == 400
