from app.models.product_image import ProductImage
from test_api_flow import (
    _auth_headers, _create_admin, _create_attribute, _create_attribute_value,
    _create_category, _create_manager, _create_material, _create_product,
    _create_public_request, _login,
)


def setup_value(client):
    _create_admin(client)
    token = _login(client, "admin", "admin12345")["access_token"]
    attribute = _create_attribute(client, token)
    value = _create_attribute_value(client, token, attribute["id"])
    return token, attribute, value


def test_forced_value_deletion_preserves_products_images_requests_and_other_values(client, db_session):
    token, attribute, value = setup_value(client)
    headers = _auth_headers(token)
    category = _create_category(client, token)
    material = _create_material(client, token)
    products = [_create_product(client, token, category["id"], material["id"], f"product-{n}") for n in range(3)]
    other = _create_attribute_value(client, token, attribute["id"])
    request = _create_public_request(client, products[0], material)
    for product in products:
        assert client.post(f"/api/products/{product['id']}/attributes/{value['id']}", headers=headers).status_code == 200
    assert client.post(f"/api/products/{products[0]['id']}/attributes/{other['id']}", headers=headers).status_code == 200
    photo = ProductImage(product_id=products[0]["id"], image_url="/static/test-photo.jpg", is_main=True)
    db_session.add(photo)
    db_session.commit()
    photo_id = photo.id
    client.patch(f"/api/products/{products[2]['id']}", headers=headers, json={"is_active": False})
    path = f"/api/attributes/values/{value['id']}"

    assert client.get(path + "/usage", headers=headers).json()["products_count"] == 3
    assert client.delete(path, headers=headers).status_code == 400
    assert client.get(path).status_code == 200
    assert client.delete(path + "?force=true", headers=headers).status_code == 200
    assert client.get(path).status_code == 404
    assert client.get(path + "/usage", headers=headers).status_code == 404
    for index, product in enumerate(products):
        response = client.get(f"/api/products/{product['id']}?include_inactive=true", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["color"] == product["color"]
        assert all(entry["id"] != value["id"] for entry in data["attributes"])
        if index == 0:
            assert [entry["id"] for entry in data["attributes"]] == [other["id"]]
            assert [image["id"] for image in data["images"]] == [photo_id]
    assert client.get(f"/api/requests/{request['id']}/details", headers=headers).status_code == 200
    assert client.get(f"/api/attributes/{attribute['id']}").status_code == 200


def test_only_admin_can_preview_usage_or_force_delete(client):
    token, _, value = setup_value(client)
    _create_manager(client, token)
    manager_headers = _auth_headers(_login(client, "manager", "manager12345")["access_token"])
    path = f"/api/attributes/values/{value['id']}"
    for headers in [{}, manager_headers]:
        assert client.get(path + "/usage", headers=headers).status_code in (401, 403)
        assert client.delete(path + "?force=true", headers=headers).status_code in (401, 403)
    assert client.get(path).status_code == 200


def test_unused_value_can_be_deleted_without_force(client):
    token, _, value = setup_value(client)
    path = f"/api/attributes/values/{value['id']}"
    headers = _auth_headers(token)
    assert client.get(path + "/usage", headers=headers).json()["products_count"] == 0
    assert client.delete(path, headers=headers).status_code == 200
