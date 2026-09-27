# Frontend Маэстро

Frontend сделан на React и собирается через Create React App. Маршрутизация работает через hash в адресе, поэтому отдельный сервер роутинга для разработки не нужен.

## Запуск и проверки

```powershell
cd frontend
npm install
npm start
```

Проверки перед передачей проекта:

```powershell
npm test -- --watchAll=false --runInBand
npm run build
npm run format:check
```

`REACT_APP_API_URL` задаёт адрес FastAPI. Шаблон находится в [.env.example](.env.example).

## Где искать нужную часть

| Что нужно изменить | Файл или папка |
| --- | --- |
| Общий каркас, маршруты и модальные заявки | [src/layouts/Site.js](src/layouts/Site.js) |
| Шапка, подвал и меню кабинета | [src/components/layout](src/components/layout) |
| Главная страница | [src/pages/public/HomePage.js](src/pages/public/HomePage.js) |
| Карусель, работы и шаги | [src/components/home](src/components/home) |
| Каталог и фильтры | [src/pages/public/CatalogPage.js](src/pages/public/CatalogPage.js), [src/components/catalog](src/components/catalog) |
| Страница проекта и форма заявки | [src/pages/public/ProductPage.js](src/pages/public/ProductPage.js), [src/components/enquiry/EnquiryDialog.js](src/components/enquiry/EnquiryDialog.js) |
| Кабинет менеджера | [src/pages/staff](src/pages/staff), [src/components/requests](src/components/requests) |
| Кабинет администратора | [src/pages/admin/AdminPage.js](src/pages/admin/AdminPage.js), [src/components/admin](src/components/admin) |
| Запросы к API и адрес backend | [src/services/api.js](src/services/api.js) |
| Тексты пяти слайдов и пути к фотографиям | [src/config/slides.js](src/config/slides.js) |
| Заглушки контактов | [src/config/contacts.js](src/config/contacts.js), [.env.example](.env.example) |
| Цвета, рамки, размеры и адаптивность | [src/styles](src/styles) |

## Организация стилей

Все стили подключаются один раз в [src/styles/index.css](src/styles/index.css). Файлы импортируются в порядке каскада:

- `base.css` — переменные, шапка, кнопки, каркас и базовые элементы;
- `common.css` — общие карточки, формы, меню и диалоги;
- `public-pages.css` — каталог, проект и публичные страницы;
- `staff.css` — кабинет сотрудников и админские таблицы;
- `responsive.css` — мобильные и широкие варианты;
- `home.css` — карусель и секции главной страницы.

В JSX нет встроенных `style={{ ... }}`: размеры, цвета и кадрирование изображений настраиваются в CSS.

## Фотографии

Пять фотографий карусели лежат в `public/carusel/` и подключаются путями `/carusel/1.png` … `/carusel/5.png` в `src/config/slides.js`. Картинки карточек каталога пока намеренно показываются компонентом `ImagePlaceholder`, чтобы их можно было заменить единообразно после наполнения API.

## Структура кода

- `components/` — переиспользуемые визуальные блоки;
- `pages/` — содержимое отдельных маршрутов;
- `layouts/` — общий каркас и кабинет;
- `hooks/` — загрузка ресурсов и действия с API;
- `context/` — авторизация сотрудника;
- `config/` — тексты и описания полей;
- `services/` — сетевой слой;
- `utils/` — чистые вспомогательные функции.

Форматирование выполняется командой `npm run format`. Настройки находятся в [.prettierrc.json](.prettierrc.json).
