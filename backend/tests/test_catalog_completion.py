import pytest

from app.routers import products
from app.models.furniture_request import FurnitureRequest
from app.models.user import User
from app.routers.furniture_requests import _assign_request_manager
from test_api_flow import (
    _auth_headers, _create_admin, _create_category, _create_manager,
    _create_material, _create_product, _create_public_request, _login,
)


def admin_session(client):
    admin = _create_admin(client)
    token = _login(client, "admin", "admin12345")["access_token"]
    return admin, token, _auth_headers(token)


def test_hidden_parent_controls_entire_storefront_without_changing_children(client):
    _, token, headers = admin_session(client)
    root = _create_category(client, token)
    child = _create_category(client, token, "child")
    leaf = _create_category(client, token, "leaf")
    for category, parent in [(child, root), (leaf, child)]:
        assert client.patch(f"/api/categories/{category['id']}", headers=headers, json={"parent_id": parent["id"]}).status_code == 200
    material = _create_material(client, token)
    product = _create_product(client, token, leaf["id"], material["id"])
    draft = _create_product(client, token, leaf["id"], material["id"], "draft")
    client.patch(f"/api/products/{draft['id']}", headers=headers, json={"is_active": False})
    previous_request = _create_public_request(client, product, material)

    assert client.get(f"/api/products/?category_id={root['id']}").json()["total"] == 0
    assert client.get(f"/api/products/?category_id={root['id']}&include_descendants=true").json()["total"] == 1
    client.patch(f"/api/categories/{root['id']}", headers=headers, json={"is_active": False})
    assert client.get("/api/catalog/options").json()["categories"] == []
    assert client.get("/api/categories/").json()["total"] == 0
    assert client.get("/api/products/").json()["total"] == 0
    for path in [f"/api/categories/{leaf['id']}", "/api/categories/slug/leaf", f"/api/products/{product['id']}", f"/api/products/slug/{product['slug']}"]:
        assert client.get(path).status_code == 404
        assert client.get(path + "?include_inactive=true", headers=headers).status_code == 200
    assert client.post("/api/requests/", json={"product_id": product["id"], "client_name": "Анна", "phone": "+79001234567", "needs_measurements": True, "personal_data_consent": True}).status_code == 404
    assert client.get(f"/api/requests/{previous_request['id']}/details", headers=headers).status_code == 200
    assert client.get(f"/api/categories/{leaf['id']}?include_inactive=true", headers=headers).json()["is_active"] is True
    client.patch(f"/api/categories/{root['id']}", headers=headers, json={"is_active": True})
    assert client.get("/api/products/").json()["total"] == 1
    assert client.get(f"/api/products/{draft['id']}").status_code == 404


@pytest.mark.parametrize("method", ["patch", "put"])
def test_category_cannot_move_into_descendant(client, method):
    _, token, headers = admin_session(client)
    root = _create_category(client, token)
    child = _create_category(client, token, "child")
    leaf = _create_category(client, token, "leaf")
    client.patch(f"/api/categories/{child['id']}", headers=headers, json={"parent_id": root["id"]})
    client.patch(f"/api/categories/{leaf['id']}", headers=headers, json={"parent_id": child["id"]})
    body = {"parent_id": leaf["id"]}
    if method == "put":
        body.update(name=root["name"], slug=root["slug"])
    assert getattr(client, method)(f"/api/categories/{root['id']}", headers=headers, json=body).status_code == 400
    assert client.get(f"/api/categories/{root['id']}").json()["parent_id"] is None
    assert client.patch(f"/api/categories/{leaf['id']}", headers=headers, json={"parent_id": None}).status_code == 200


def test_managers_cannot_take_or_unassign_someone_elses_request(client):
    _, token, headers = admin_session(client)
    first = _create_manager(client, token)
    second = _create_manager(client, token, login="second")
    first_headers = _auth_headers(_login(client, "manager", "manager12345")["access_token"])
    second_headers = _auth_headers(_login(client, "second", "manager12345")["access_token"])
    response = client.post("/api/requests/", json={"product_name": "Кухня", "client_name": "Анна", "phone": "+79001234567", "needs_measurements": True, "personal_data_consent": True})
    assert response.status_code == 200
    path = f"/api/requests/{response.json()['id']}"
    assert client.patch(path + "/take", headers=first_headers).json()["assigned_manager_id"] == first["id"]
    assert client.patch(path + "/take", headers=second_headers).status_code == 403
    for suffix in ["", "/manager"]:
        for manager_id in [None, second["id"]]:
            assert client.patch(path + suffix, headers=second_headers, json={"assigned_manager_id": manager_id}).status_code == 403
    assert client.get(path, headers=headers).json()["assigned_manager_id"] == first["id"]
    assert client.patch(path + "/manager", headers=first_headers, json={"assigned_manager_id": None}).status_code == 200
    assert client.patch(path + "/take", headers=second_headers).status_code == 200
    assert client.patch(path + "/manager", headers=headers, json={"assigned_manager_id": first["id"]}).status_code == 200


def test_last_admin_keeps_access_to_administration(client):
    admin, token, headers = admin_session(client)
    path = f"/api/users/{admin['id']}"
    assert client.patch(path, headers=headers, json={"role": "manager"}).status_code == 400
    assert client.delete(path, headers=headers).status_code == 400
    other = _create_manager(client, token, login="other")
    assert client.patch(f"/api/users/{other['id']}", headers=headers, json={"role": "admin"}).status_code == 200
    assert client.patch(path, headers=headers, json={"role": "manager"}).status_code == 200
    assert client.get("/api/users/", headers=headers).status_code == 403


def test_reassignment_uses_current_database_owner_when_request_was_loaded_earlier(client, db_session):
    admin, token, headers = admin_session(client)
    first = _create_manager(client, token)
    second = _create_manager(client, token, login="second")
    request = client.post("/api/requests/", json={"product_name": "Кухня", "client_name": "Анна", "phone": "+79001234567", "needs_measurements": True, "personal_data_consent": True}).json()
    path = f"/api/requests/{request['id']}/manager"
    client.patch(path, headers=headers, json={"assigned_manager_id": first["id"]})
    stale_request = db_session.get(FurnitureRequest, request["id"])
    client.patch(path, headers=headers, json={"assigned_manager_id": second["id"]})
    _assign_request_manager(stale_request, first["id"], db_session.get(User, admin["id"]), db_session)
    db_session.commit()
    assert client.get(f"/api/requests/{request['id']}", headers=headers).json()["assigned_manager_id"] == first["id"]


def test_image_cleanup_stays_inside_upload_directory(tmp_path, monkeypatch):
    upload = tmp_path / "uploads"
    upload.mkdir()
    outside = tmp_path / "keep.txt"
    outside.write_text("keep", encoding="utf-8")
    image = upload / "photo.png"
    image.write_bytes(b"test")
    monkeypatch.setattr(products, "UPLOAD_ROOT", upload)
    for url in ["/static/uploads/products/../keep.txt", "/static/uploads/products/..\\keep.txt", "/static/uploads/products-other/../keep.txt"]:
        products._delete_uploaded_image_file(url)
        assert outside.exists()
    products._delete_uploaded_image_file("/static/uploads/products/photo.png")
    assert not image.exists()
