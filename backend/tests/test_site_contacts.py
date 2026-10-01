import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect

from test_api_flow import _auth_headers, _create_admin, _create_manager, _login


def admin_headers(client):
    _create_admin(client)
    token = _login(client, "admin", "admin12345")["access_token"]
    return token, _auth_headers(token)


def test_contacts_are_public_persistent_and_can_be_cleared(client):
    assert client.get('/api/site/contacts').json() == {
        'configured': False, 'phone': None, 'address': None, 'hours': None, 'email': None,
    }
    _, headers = admin_headers(client)
    response = client.put('/api/site/contacts', headers=headers, json={
        'phone': ' +7 (900) 123-45-67 ', 'address': ' ул. Мебельная, 1 ',
        'hours': 'Пн–Пт: 9–18\nСб: 10–16', 'email': ' hello@example.com ',
    })
    assert response.status_code == 200
    saved = response.json()
    assert saved['configured'] is True
    assert saved['phone'] == '+7 (900) 123-45-67'
    assert saved['email'] == 'hello@example.com'
    assert client.get('/api/site/contacts').json() == saved
    assert client.put('/api/site/contacts', headers=headers, json={'phone': '   '}).status_code == 200
    assert client.get('/api/site/contacts').json() == {
        'configured': True, 'phone': None, 'address': None, 'hours': None, 'email': None,
    }


def test_contacts_cannot_be_changed_by_visitors_or_managers(client):
    token, _ = admin_headers(client)
    _create_manager(client, token)
    manager_headers = _auth_headers(_login(client, 'manager', 'manager12345')['access_token'])
    for headers in [{}, manager_headers]:
        assert client.put('/api/site/contacts', headers=headers, json={'address': 'Подмена'}).status_code in (401, 403)
    assert client.get('/api/site/contacts').json()['configured'] is False


@pytest.mark.parametrize('body', [{'email': 'not-an-email'}, {'phone': '123'}, {'address': 'x' * 501}])
def test_contacts_validate_input(client, body):
    _, headers = admin_headers(client)
    assert client.put('/api/site/contacts', headers=headers, json=body).status_code == 422
    assert client.get('/api/site/contacts').json()['configured'] is False


def test_contacts_migration_creates_and_removes_only_its_table():
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/d2e3f4a5b6c7_add_site_contacts.py'
    spec = importlib.util.spec_from_file_location('contacts_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        connection.exec_driver_sql('CREATE TABLE existing_data (id INTEGER PRIMARY KEY)')
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            assert set(inspect(connection).get_table_names()) == {'existing_data', 'site_contacts'}
            assert {column['name'] for column in inspect(connection).get_columns('site_contacts')} == {'id', 'phone', 'address', 'hours', 'email'}
            migration.downgrade()
            assert inspect(connection).get_table_names() == ['existing_data']
    engine.dispose()
