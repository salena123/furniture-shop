# Furniture Shop

Backend на FastAPI для мебельного сайта с публичным каталогом, заявками с сайта и личным кабинетом сотрудников.

## Что уже есть

- JWT-авторизация для сотрудников.
- Роли: `admin` и `manager`.
- Публичный каталог: категории, материалы, товары, характеристики.
- Публичное создание заявок без авторизации.
- Личный кабинет менеджера: список заявок, назначение ответственного, статусы, комментарии.
- Админские CRUD-роуты для наполнения каталога.
- Seed-скрипт для стартовых данных.
- API-тесты на основные сценарии.

## Backend

Команды выполнять из корня проекта:

```powershell
cd backend
venv\Scripts\pip.exe install -r requirements.txt
venv\Scripts\python.exe -m alembic upgrade head
venv\Scripts\python.exe seed.py
venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Проверка базы:

```text
http://127.0.0.1:8000/test-db
```

## Переменные окружения

Шаблон лежит в [.env.example](.env.example). Настоящий `.env` хранит локальные пароли и не должен попадать в git.

Основные переменные:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/furniture_shop
SECRET_KEY=change-me-long-random-secret-at-least-32-bytes
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
MAX_IMAGE_SIZE_BYTES=5242880
```

`SECRET_KEY` нужен для подписи JWT. В реальном проекте он должен быть длинным и случайным.

После изменений структуры БД запускать миграции:

```powershell
cd backend
venv\Scripts\python.exe -m alembic upgrade head
```

## Seed

Seed-скрипт заполняет базу стартовыми данными для разработки:

```powershell
cd backend
venv\Scripts\python.exe seed.py
```

После запуска появятся пользователи:

```text
admin / admin12345
manager / manager12345
```

Также создаются категории, материалы, атрибуты, товары и тестовые заявки.

## Авторизация в Swagger

1. Открыть `/api/auth/login`.
2. Ввести логин и пароль сотрудника.
3. Скопировать `access_token`.
4. Нажать кнопку `Authorize` вверху Swagger.
5. Вставить только сам токен, без слова `Bearer`.

В коде фронта токен отправляется так:

```js
headers: {
  Authorization: `Bearer ${token}`,
}
```

## Тесты

Из корня проекта:

```powershell
backend\venv\Scripts\python.exe -m pytest -q
```

Тесты используют отдельную SQLite-базу во временной папке и не трогают рабочую БД.

## API-контракт

Карта endpoint'ов для фронта лежит здесь:

[docs/api-contract.md](docs/api-contract.md)
