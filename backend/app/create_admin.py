"""Local-only initial administrator setup: python -m app.create_admin."""
from getpass import getpass

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password


def main():
    with SessionLocal() as db:
        if db.query(User).filter(User.role == 'admin').first():
            raise SystemExit('Администратор уже есть. Создавайте сотрудников через кабинет.')
        login = input('Логин администратора: ')
        name = input('Имя: ')
        password = getpass('Пароль (не отображается): ')
        if password != getpass('Повторите пароль: '):
            raise SystemExit('Пароли не совпадают')
        try:
            data = UserCreate(login=login, name=name, password=password, role='admin')
        except ValueError:
            raise SystemExit('Проверьте логин и пароль: логин 3–100 символов, пароль 8–256 символов.')
        if db.query(User).filter(User.login == data.login).first():
            raise SystemExit('Логин уже занят')
        db.add(User(login=data.login, name=data.name, password_hash=hash_password(data.password), role='admin'))
        db.commit()
        print('Администратор создан')


if __name__ == '__main__':
    main()
