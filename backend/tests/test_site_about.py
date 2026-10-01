import base64
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect

from app.routers import site_about
from test_api_flow import _auth_headers, _create_manager, _login
from test_site_contacts import admin_headers

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aD1sAAAAASUVORK5CYII=')


def test_about_upload_preview_publish_and_clear(client, monkeypatch, tmp_path):
    monkeypatch.setattr(site_about, 'UPLOAD_ROOT', tmp_path)
    original = client.get('/api/site/about').json()
    assert original['configured'] is False
    _, headers = admin_headers(client)
    response = client.post('/api/site/about/images', headers=headers, files={'file': ('../photo.png', PNG, 'image/png')})
    assert response.status_code == 201
    image_url = response.json()['image_url']
    assert (tmp_path / image_url.rsplit('/', 1)[1]).read_bytes() == PNG
    assert client.get('/api/site/about').json() == original  # Upload is not publication.
    page = {'title': 'О мастерской', 'blocks': [
        {'type': 'text', 'text': '## Наши работы\n\n**Мебель** на заказ'},
        {'type': 'image', 'image_url': image_url, 'caption': 'Мастерская', 'alt': 'Рабочее место'},
    ]}
    assert client.put('/api/site/about', headers=headers, json=page).status_code == 200
    assert client.get('/api/site/about').json() == {**page, 'configured': True}
    page['blocks'].reverse()
    assert client.put('/api/site/about', headers=headers, json=page).status_code == 200
    assert client.get('/api/site/about').json()['blocks'][0]['type'] == 'image'
    assert client.put('/api/site/about', headers=headers, json={'title': 'О нас', 'blocks': []}).status_code == 200
    assert client.get('/api/site/about').json()['blocks'] == []


def test_about_requires_admin_for_publish_and_upload(client):
    token, _ = admin_headers(client)
    _create_manager(client, token)
    manager = _auth_headers(_login(client, 'manager', 'manager12345')['access_token'])
    for headers in ({}, manager):
        assert client.put('/api/site/about', headers=headers, json={'title': 'Подмена', 'blocks': []}).status_code in (401, 403)
        assert client.post('/api/site/about/images', headers=headers, files={'file': ('photo.png', PNG, 'image/png')}).status_code in (401, 403)
    assert client.get('/api/site/about').json()['configured'] is False


def test_about_rejects_unsafe_paths_missing_images_and_bad_uploads(client, monkeypatch, tmp_path):
    monkeypatch.setattr(site_about, 'UPLOAD_ROOT', tmp_path)
    _, headers = admin_headers(client)
    for url in ['https://example.com/test.png', '/static/uploads/about/../test.png', 'javascript:alert(1)']:
        assert client.put('/api/site/about', headers=headers, json={'title': 'О нас', 'blocks': [{'type': 'image', 'image_url': url}]}).status_code == 422
    assert client.put('/api/site/about', headers=headers, json={'title': 'О нас', 'blocks': [{'type': 'image', 'image_url': '/static/uploads/about/' + 'a' * 32 + '.png'}]}).status_code == 400
    for content in [b'', b'<svg onload="alert(1)"></svg>', b'x' * (site_about.MAX_IMAGE_SIZE + 1)]:
        assert client.post('/api/site/about/images', headers=headers, files={'file': ('fake.png', content, 'image/png')}).status_code == 400
    assert not list(tmp_path.iterdir())
    assert client.put('/api/site/about', headers=headers, json={'title': ' ', 'blocks': []}).status_code == 422
    assert client.put('/api/site/about', headers=headers, json={'title': 'О нас', 'blocks': [{'type': 'text', 'text': 'x'}] * 51}).status_code == 422


def test_about_migration():
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/e3f4a5b6c7d8_add_site_about.py'
    spec = importlib.util.spec_from_file_location('about_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        connection.exec_driver_sql('CREATE TABLE existing_data (id INTEGER PRIMARY KEY)')
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            assert set(inspect(connection).get_table_names()) == {'existing_data', 'site_about'}
            migration.downgrade()
            assert inspect(connection).get_table_names() == ['existing_data']
    engine.dispose()
