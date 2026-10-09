from test_api_flow import _auth_headers, _create_category, _create_material, _create_product, _login

PNG = b"\x89PNG\r\n\x1a\n" + b"test-image"


def _public_request(client, **extra):
    body = {
        'product_name': 'Кухня',
        'client_name': 'Анна',
        'phone': '+79001234567',
        'needs_measurements': True,
        'personal_data_consent': True,
    }
    body.update(extra)
    return client.post('/api/requests/', json=body)


def test_public_request_honeypot_and_rate_limit(client):
    assert _public_request(client, website='https://bot.example').status_code == 400
    for _ in range(10):
        assert _public_request(client).status_code == 200
    limited = _public_request(client)
    assert limited.status_code == 429
    assert limited.headers['retry-after']


def test_product_upload_checks_file_signature(client, tmp_path, monkeypatch):
    monkeypatch.setattr('app.routers.products.UPLOAD_ROOT', tmp_path)
    from test_api_flow import _create_admin

    _create_admin(client)
    token = _login(client, 'admin', 'admin12345')['access_token']
    category = _create_category(client, token)
    material = _create_material(client, token)
    product = _create_product(client, token, category['id'], material['id'])
    headers = _auth_headers(token)
    mismatch = client.post(
        f"/api/products/{product['id']}/images/upload",
        headers=headers,
        files={'file': ('photo.jpg', PNG, 'image/jpeg')},
    )
    assert mismatch.status_code == 400
    valid = client.post(
        f"/api/products/{product['id']}/images/upload",
        headers=headers,
        files={'file': ('photo.png', PNG, 'image/png')},
    )
    assert valid.status_code == 200


def test_security_headers_are_present(client):
    response = client.get('/')
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert response.headers['x-frame-options'] == 'DENY'
    assert "frame-ancestors 'none'" in response.headers['content-security-policy']
