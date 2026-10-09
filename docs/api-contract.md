# API Contract

Base URL для локальной разработки:

```text
http://127.0.0.1:8000
```

Защищённые endpoint'ы требуют заголовок:

```http
Authorization: Bearer <access_token>
```

## Формат списков

Списочные endpoint'ы возвращают объект:

```json
{
  "items": [],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

`total` показывает количество записей с учётом фильтров, но без `limit` и `offset`.

## Авторизация

### POST `/api/auth/login`

Публичный endpoint для входа сотрудника.

Request:

```json
{
  "login": "admin",
  "password": "admin12345"
}
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "expires_in": 86400,
  "expires_at": "2026-09-16T12:00:00Z",
  "user": {
    "id": 1,
    "login": "admin",
    "name": "Администратор",
    "email": null,
    "role": "admin",
    "last_login_at": "2026-09-16T11:00:00Z"
  }
}
```

### GET `/api/auth/me`

Роли: `admin`, `manager`.

Возвращает текущего пользователя по JWT.

## Публичный каталог

### GET `/api/catalog/options`

Публичный endpoint для форм и фильтров.

Response:

```json
{
  "categories": [],
  "materials": [],
  "attributes": []
}
```

### GET `/api/categories/`

Публично возвращает только активные категории.

Query:

```text
parent_id?: number
include_inactive?: boolean
limit?: number
offset?: number
```

`include_inactive=true` доступен только админу.

### GET `/api/categories/{category_id}`

Публичная карточка категории.

### GET `/api/categories/slug/{slug}`

Публичная карточка категории по slug.

### GET `/api/materials/`

Публичный список материалов.

Query:

```text
search?: string
limit?: number
offset?: number
```

### GET `/api/materials/{material_id}`

Публичная карточка материала.

### GET `/api/products/`

Публичный список активных товаров.

Query:

```text
category_id?: number
include_descendants?: boolean
material_id?: number
search?: string
include_inactive?: boolean
limit?: number
offset?: number
```

`include_inactive=true` доступен только админу.

`include_descendants=true` включает товары всех вложенных подкатегорий. По умолчанию фильтр `category_id` выбирает только указанную категорию. Публичные списки, карточки по ID/slug и заявки доступны только для опубликованных товаров с полностью опубликованной цепочкой категорий. Скрытие родительской категории не меняет собственные флаги публикации потомков.

### GET `/api/products/{product_id}`

Публичная карточка товара.

### GET `/api/products/slug/{slug}`

Публичная карточка товара по slug.

### GET `/api/products/{product_id}/images`

Публичный список фотографий товара.

### GET `/api/products/{product_id}/attributes`

Публичный список характеристик товара.

## Публичные заявки

### POST `/api/requests/`

Публичное создание заявки без авторизации.

Request:

```json
{
  "product_id": 1,
  "material_id": 2,
  "needs_measurements": true,
  "dimensions": "3200 мм",
  "client_name": "Анна",
  "phone": "+7 900 100-20-30",
  "city": "Екатеринбург",
  "preferred_contact_time": "после 14:00",
  "personal_data_consent": true,
  "comment": "Перезвонить после обеда"
}
```

`product_id` и `material_id` необязательные. Если `product_id` передан, название, цвет и материал подтянутся из товара. Если `product_id` не передан, нужно отправить `product_name` вручную.

`personal_data_consent` должен быть `true`, иначе заявка не создаётся.

## Кабинет менеджера

Роли: `admin`, `manager`.

### GET `/api/dashboard/stats`

Статистика для кабинета.

### GET `/api/requests/statuses`

Список доступных статусов заявки.

### GET `/api/requests/`

Список заявок.

Query:

```text
status?: new | in_progress | contacted | measurement_scheduled | quote_prepared | completed | cancelled
assigned_manager_id?: number
unassigned_only?: boolean
product_id?: number
material_id?: number
phone?: string
city?: string
search?: string
limit?: number
offset?: number
```

Элемент `items` содержит:

```json
{
  "id": 1,
  "product_id": 1,
  "product_slug": "kuhnya-praktika",
  "category_id": 1,
  "category_name": "Кухни",
  "material_id": 1,
  "material_name": "МДФ",
  "product_name": "Кухня Практика",
  "client_name": "Анна",
  "phone": "+7 900 100-20-30",
  "city": "Екатеринбург",
  "preferred_contact_time": "после 14:00",
  "personal_data_consent": true,
  "status": "new",
  "assigned_manager_id": null,
  "assigned_manager_name": null,
  "comments_count": 0,
  "events_count": 0
}
```

### GET `/api/requests/my`

Заявки, назначенные на текущего сотрудника.

Query:

```text
status?: string
limit?: number
offset?: number
```

### GET `/api/requests/{request_id}`

Краткая карточка заявки.

### GET `/api/requests/{request_id}/details`

Полная карточка заявки: заявка, менеджер, товар, комментарии, история событий.

### PATCH `/api/requests/{request_id}`

Частичное обновление заявки.

Request:

```json
{
  "status": "contacted",
  "assigned_manager_id": 2,
  "city": "Екатеринбург",
  "preferred_contact_time": "после 18:00",
  "comment": "Общий комментарий клиента"
}
```

### PATCH `/api/requests/{request_id}/status`

Ручная смена статуса менеджером.

Request:

```json
{
  "status": "contacted"
}
```

### PATCH `/api/requests/{request_id}/manager`

Назначение ответственного.

Request:

```json
{
  "assigned_manager_id": 2
}
```

Менеджер может назначить заявку только на себя или снять себя с заявки. Админ может назначать любого сотрудника.

### PATCH `/api/requests/{request_id}/take`

Текущий сотрудник берёт заявку на себя.

### GET `/api/requests/{request_id}/comments`

Комментарии по заявке.

### POST `/api/requests/{request_id}/comments`

Request:

```json
{
  "comment_text": "Клиент ждёт расчёт"
}
```

### PUT `/api/requests/{request_id}/comments/{comment_id}`

Редактирование комментария. Админ может редактировать любой, менеджер только свой.

### DELETE `/api/requests/{request_id}/comments/{comment_id}`

Удаление комментария. Админ может удалить любой, менеджер только свой.

### GET `/api/requests/{request_id}/events`

История событий заявки.

## Админка

Роль: `admin`.

### Пользователи

- `POST /api/users/bootstrap-admin` - создать первого администратора, только если пользователей ещё нет.
- `POST /api/users/` - создать сотрудника.
- `GET /api/users/` - список пользователей.
- `GET /api/users/managers` - список сотрудников, которых можно назначать на заявки.
- `GET /api/users/{user_id}` - карточка пользователя.
- `PUT /api/users/{user_id}` - полное обновление.
- `PATCH /api/users/{user_id}` - частичное обновление.
- `DELETE /api/users/{user_id}` - удалить пользователя.

Пользователь не удаляется, если у него есть комментарии или события заявок. Если у него только назначенные заявки, они отвязываются.

### Категории

- `POST /api/categories/`
- `PUT /api/categories/{category_id}`
- `PATCH /api/categories/{category_id}`
- `DELETE /api/categories/{category_id}`

Категория не удаляется, если у неё есть подкатегории или товары.

### Материалы

- `POST /api/materials/`
- `PUT /api/materials/{material_id}`
- `PATCH /api/materials/{material_id}`
- `DELETE /api/materials/{material_id}`

При удалении материала он отвязывается от товаров и заявок.

### Товары

- `POST /api/products/`
- `PUT /api/products/{product_id}`
- `PATCH /api/products/{product_id}`
- `DELETE /api/products/{product_id}`
- `POST /api/products/{product_id}/images`
- `POST /api/products/{product_id}/images/upload`
- `PUT /api/products/images/{image_id}`
- `DELETE /api/products/images/{image_id}`
- `POST /api/products/{product_id}/attributes/{attribute_value_id}`
- `DELETE /api/products/{product_id}/attributes/{attribute_value_id}`

`DELETE /api/products/{product_id}` не удаляет товар физически, а скрывает его с сайта через `is_active=false`. История заявок и связь с товаром сохраняются.

Загрузка изображений:

- разрешены `jpg`, `png`, `webp`, `gif`;
- максимальный размер задаётся переменной `MAX_IMAGE_SIZE_BYTES`;
- если загружается первая фотография товара, она автоматически становится главной;
- если новая фотография помечена как главная, предыдущая главная автоматически перестаёт быть главной.

### Атрибуты

- `POST /api/attributes/`
- `PUT /api/attributes/{attribute_id}`
- `PATCH /api/attributes/{attribute_id}`
- `DELETE /api/attributes/{attribute_id}`
- `POST /api/attributes/{attribute_id}/values`
- `PUT /api/attributes/values/{value_id}`
- `PATCH /api/attributes/values/{value_id}`
- `DELETE /api/attributes/values/{value_id}`
- `GET /api/attributes/values/{value_id}/usage` — только администратор; возвращает `id`, `value`, `products_count` (включая скрытые товары).

По умолчанию удаление используемого значения возвращает `400`. После явного подтверждения администратор может вызвать `DELETE /api/attributes/values/{value_id}?force=true`: удаляются значение и его связи с товарами в одной транзакции. Товары, их основные поля, фотографии, заявки и другие значения сохраняются. Удаление самой характеристики целиком по-прежнему блокируется, если её значения используются.

Атрибут или значение нельзя удалить, пока оно используется у товара.

## Валидация

- `slug` только латиница в нижнем регистре, цифры и дефисы.
- `phone` должен быть похож на номер телефона.
- Обязательные строки не могут быть пустыми или состоять только из пробелов.
- Опциональные строки очищаются от пробелов; пустая строка становится `null`.
- `sort_order` не может быть отрицательным.
- id связей должны быть положительными числами.
- для публичной заявки `personal_data_consent` должен быть `true`.

## Ошибки

Ошибки возвращаются в едином формате:

```json
{
  "error": "validation_error",
  "message": "Ошибка валидации данных",
  "detail": []
}
```

Частые коды:

- `400 bad_request` - ошибка бизнес-логики.
- `401 unauthorized` - нет токена или токен неверный.
- `403 forbidden` - недостаточно прав.
- `404 not_found` - запись не найдена.
- `422 validation_error` - тело запроса не прошло валидацию.

## Авторизация и безопасность

- `POST /api/auth/login` принимает логин и пароль, устанавливает `HttpOnly` cookie и не возвращает токен в JSON. На вход действуют ограничения частоты попыток по IP и логину.
- `GET /api/auth/me` проверяет подпись JWT, обязательные `exp`, `iat`, `jti` и версию учётной записи, а также активную серверную сессию.
- `POST /api/auth/logout` отзывает текущую серверную сессию и удаляет cookie.
- Изменение пароля отзывает все сессии сотрудника. Для запросов из frontend используется заголовок `X-CSRF-Protection: 1`; список разрешённых источников задаётся через `CORS_ORIGINS`.
- Пароли хранятся в формате `pbkdf2_sha256` с солью и 600 000 итерациями. Старые корректные PBKDF2-хэши усиливаются при следующем входе.
- Публичный `POST /api/requests/` принимает скрытое поле `website` для honeypot-проверки; заполненное поле отклоняется. Для одного IP разрешено не более 10 заявок за 15 минут.
- Загрузки фотографий принимаются только при совпадении MIME-типа и сигнатуры файла (JPG, PNG, WebP или GIF).

## Контакты сайта

- `GET /api/site/contacts` — публичные поля `phone`, `address`, `hours`, `email`, а также `configured` (было ли первое сохранение).
- `PUT /api/site/contacts` — только администратор; полная замена четырёх полей. Пробелы по краям удаляются, пустые строки сохраняются как `null`. Телефон и почта валидируются, длина полей ограничена. Ответ содержит сохранённые поля и `configured: true`.

До первого сохранения API возвращает пустые поля и `configured: false`. Настройки хранятся в таблице `site_contacts` (миграция `d2e3f4a5b6c7`).

## Страница «О нас»

- `GET /api/site/about` — публичные `title`, `blocks`, `configured`. До первой публикации возвращает начальное содержание без записи в БД.
- `PUT /api/site/about` — только администратор, публикация полной страницы: `title` (1–200 символов), `blocks` (до 50 блоков).
- Текстовый блок: `{ "type": "text", "text": "## Заголовок\n\nТекст" }`, до 20 000 символов. Поддерживается ограниченное форматирование: заголовки, жирный, курсив, списки, ссылки. HTML отображается как текст.
- Фотография: `{ "type": "image", "image_url": "/static/uploads/about/<uuid>.png", "caption": "Подпись", "alt": "Описание" }`. Подпись до 500 символов, alt до 300. Разрешены только существующие файлы загрузок страницы.
- `POST /api/site/about/images` — только администратор, multipart `file`, JPG/PNG/WebP до 10 МБ. Проверяется сигнатура файла; возвращает `{ "image_url": "..." }` со статусом 201. Сам по себе файл на странице не публикуется.

Таблица `site_about`, миграция `e3f4a5b6c7d8`. Текст и порядок блоков хранятся в JSON, фотографии — в `backend/static/uploads/about`. Удалённые из содержания файлы сохраняются на диске; автоматическая очистка не выполняется. Резервная копия должна включать БД и папку загрузок.
