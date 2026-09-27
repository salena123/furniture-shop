# Промпты визуальной концепции

Финальная правка 02-catalog: по изображениям главной (референс) и каталога (цель правки) унифицированы логотип, белая строка навигации, кнопки и подвал; исходный контент каталога сохранён.

Использован встроенный ImageGen. Четыре растровых концепта; не редактируемый файл Figma. Основа: просмотренный макет пользователя, https://www.figma.com/design/Os7ttoybn7cV9SetSpSThv/ (node 0:1). Живой mebelmaestro.ru показал проверку доступа, она не проходилась. Имена, карточки работ и номера заявок — демонстрационные.

## 01-home

```text
Use case: ui-mockup
Asset type: high-fidelity Russian desktop furniture company website homepage, straight-on clean screenshot, approximately 1600 x 1152.
Primary request: Create a polished, realistically buildable redesign of the user's simplified МАЭСТРО furniture website. The reference was visually inspected: white background, a compact logo on left, green About and Contacts buttons in header, red login button, and a big image carousel featuring a dark red kitchen with white caption and red order button. Preserve that recognizable structure while improving typography, balance and spacing. This is one finished web page, no Figma chrome, no perspective, no device shell, no mood board.
Visual system: white surfaces, subtle warm grey #F6F7F4, forest green #16734D for navigation, burgundy #A52C36 for the main request action, dark text #202622, muted grey secondary text. Clean modern Manrope-like sans typography with highly legible Cyrillic, generous margins and 12px rounding only on controls. Restrained professional regional custom furniture brand, no unnecessary luxury ornaments.
Composition: Entire page fully visible with about 72px outer margins. Header 100px tall. Left a compact typographic logo "МАЭСТРО" with tiny green, ochre and burgundy geometric furniture silhouettes above, descriptor "Мебель на заказ". Header right two calm green buttons "О нас", "Контакты", plus outlined login with user icon "Войти".
Below header one simple category navigation row: green button with hamburger icon "Каталог"; links "Кухни", "Шкафы", "Гардеробные", "Гостиные", "Прихожие"; subtle downward chevrons where applicable. Thin dividing rule.
Main dominant wide hero carousel, about 600px tall: photoreal architectural interior of a custom modern burgundy handleless fitted kitchen, matte wine red cabinetry, dark charcoal marble backsplash, warm wood floor, warm task lights and daylight; realistic proportions, not a stock photo collage. Add a subtle dark gradient ONLY on the left for white copy. Large clear left headline on two lines exactly "Мебель для вашего дома". Smaller line "По вашим размерам и пожеланиям". Burgundy CTA "Оставить заявку". Small light line below "Обсудим ваш проект и подберём материалы". Round previous/next arrow buttons at hero edges. Small slide indicator bottom right "01 / 03". No unverified commercial offers or promises.
Directly below photo create 3 equal clickable carousel caption tabs separated by thin rules, with small numbers: active green underline "01  Кухни", "02  Шкафы", "03  Гардеробные"; each with a quiet short line respectively "Продумано до мелочей", "Порядок в каждой детали", "Место для всего". This is carousel navigation, no extra photo grid.
Small white footer with thin line: "МАЭСТРО", "Мебель на заказ", links "О нас" and "Контакты", muted "Для сотрудников".
Constraints: only header, category navigation, hero carousel with captions, small footer. Do not add reviews, statistics, promotions, cart, prices, testimonials, services grid, newsletter, floating chat or invented phone/address. Russian text must be readable and accurate. UI fills image. Strong visual hierarchy, consistent baseline grid.
```

## 02-catalog

```text
Use case: ui-mockup
Asset type: high-fidelity Russian desktop furniture portfolio catalog webpage screenshot, approximately 1600 x 1152.
Primary request: Create the catalog screen for МАЭСТРО custom furniture company, emphasizing categories -> subcategories -> completed works. Design a fully legible realistic flat web page, not a device mockup or moodboard.
Shared design system: white, subtle warm grey #F6F7F4, forest green #16734D primary nav, burgundy #A52C36 request buttons, dark #202622. Manrope-like modern sans with perfect Cyrillic. Spacious professional furniture site, 72px outer margins, subtle 12px corner radii.
Header same system as homepage: left logo "МАЭСТРО", small descriptor "Мебель на заказ", right green buttons "О нас", "Контакты", outlined "Войти". Second nav row "Каталог", "Кухни", "Шкафы", "Гардеробные", "Гостиные", "Прихожие".
Page title zone: breadcrumb "Главная / Каталог / Кухни / Угловые", large headline "Угловые кухни", short subtitle "Выполненные проекты для вашего вдохновения".
Left 240px category sidebar titled "Каталог мебели". Expanded category "Кухни" with nested links "Все кухни", "Прямые", active pale green "Угловые", "П-образные", "С островом". Other collapsed categories "Шкафы", "Гардеробные", "Гостиные", "Прихожие". Clearly show nesting using indentation. No excessive icons.
Right main area: quiet results text "4 работы"; compact filter pills "Все материалы", "Все стили", control "Сначала новые". Large 2 by 2 card grid. Each card has a large carefully photographed real interior, slim small caption underneath, no heavy shadows: first burgundy L-shaped modern custom kitchen with charcoal marble; second off-white and oak L-shaped kitchen with bright daylight; third sage green kitchen with pale stone countertop; fourth warm walnut and beige kitchen. Distinct complete interior compositions. Card captions exact: "Кухня «Гранат»" / "Эмаль · Современный стиль"; "Кухня «Тёплый дуб»" / "МДФ и шпон · Современный стиль"; "Кухня «Шалфей»" / "Эмаль · Неоклассика"; "Кухня «Лён»" / "МДФ · Минимализм". Each has discreet text link "Подробнее ↗". One small tag "Выполненный проект" on photos.
Small footer with МАЭСТРО, О нас, Контакты, Для сотрудников.
Constraints: portfolio and custom-made product catalog, no cart, no ecommerce prices, no discounts, no ratings, no invented commercial stats. Crisp aligned grid. Give photo cards enough room and make subcategory hierarchy obvious.
```

## 03-manager

```text
Use case: ui-mockup
Asset type: high-fidelity Russian desktop internal employee workspace UI screenshot, approximately 1600 x 1100.
Primary request: Design the manager personal account for МАЭСТРО custom furniture company. The core is incoming customer enquiries, responsible manager, statuses and internal comments. One professional usable screen, no device shell, no decoration, no charts.
Shared brand style: white surfaces, light grey #F6F7F4 workspace, forest green #16734D primary actions, burgundy #A52C36 used only sparingly for attention, dark #202622, Manrope-like sans with accurate Cyrillic, generous but efficient spacing, thin borders and subtle 10px corners.
Layout: 216px left navigation sidebar white, top brand "МАЭСТРО", small "Кабинет сотрудника". Sidebar selected pale green "Заявки", then "Профиль". Bottom links "Открыть сайт ↗", "Выйти". Main upper toolbar white, role badge "Менеджер", right avatar initials "АК" and name "Анна К.".
Main content header left large "Заявки" with subtitle "Обращения клиентов и история общения", right green button "+ Новая заявка". Below tab filters "Все", selected "Мои", "Без ответственного"; search input "Имя, телефон или номер заявки", dropdown "Все статусы".
Below main region split 60/40: left a white enquiries list table and right open selected enquiry card. Table header "Заявка", "Клиент", "Статус"; five spacious rows with exact samples:
"№ 1048" / "Угловая кухня" / "Елена П." / pale green badge "Новая";
"№ 1047" / "Шкаф в прихожую" / "Дмитрий С." / pale gold badge "В работе";
"№ 1046" / "Кухня с островом" / "Ольга М." / pale gold "В работе";
"№ 1045" / "Гардеробная" / "Иван Р." / pale grey "Завершена";
"№ 1044" / "Прямая кухня" / "Мария К." / pale grey "Завершена".
Selected first row pale green with left slim green marker.
Detail panel top small "Заявка № 1048", big "Угловая кухня", "Елена П." and clearly masked placeholder phone "+7 (•••) •••-••-••". Small link "Кухня «Гранат» ↗". Status labeled "Статус" dropdown "Новая"; assignee labeled "Ответственный" read-only text "Анна К." and subtle action link "Снять с себя" (manager cannot assign other people). Section "Пожелания клиента" with clear short text "Нужна угловая кухня в светлых тонах. Есть план помещения." Thin divider, heading "Комментарии", one sample internal note "Анна К. · сегодня, 10:30" and "Уточнить размеры помещения и материал фасадов." Comment input placeholder "Добавить комментарий…" and green button "Отправить". Detail footer green "Сохранить".
Small subtle bottom label "Демонстрационные данные".
Constraints: show only manager tools; NO employee management, finances, statistics charts, excessive KPIs, product editing controls or designer/master role. All names and numbers are fictional demo data. All UI copy is Russian, polished readable typography.
```

## 04-admin

```text
Use case: ui-mockup
Asset type: high-fidelity Russian desktop admin personal account screenshot, approximately 1600 x 1100.
Primary request: Design the МАЭСТРО administrator workspace for maintaining a custom furniture catalog and categories. Same brand and components as manager workspace. One clear realistic screen, not a mood board.
Visual system: white surfaces, light grey #F6F7F4 workspace, forest green #16734D primary actions, dark #202622 text, burgundy #A52C36 used only as a tiny accent. Manrope-like modern sans with flawless Cyrillic. Thin borders, 10px corners, restrained professional whitespace.
Layout: 216px left white sidebar, top brand "МАЭСТРО" and "Кабинет сотрудника". Menu: "Заявки", selected pale green "Каталог", "Сотрудники", "Профиль". Bottom "Открыть сайт ↗", "Выйти". Upper toolbar white with role badge "Администратор", avatar initials "АМ".
Content header title "Каталог", subtitle "Категории, товары и выполненные работы", right green primary "+ Добавить работу".
Below two tabs active "Работы" and "Категории". Search field "Найти работу…" and dropdown "Все категории". Below a broad white card with two side-by-side areas: left slim category tree headed "Категории", right main item table.
Tree: expanded "Кухни", nested "Прямые", selected pale green "Угловые", "П-образные", "С островом"; collapsed "Шкафы", "Гардеробные", "Гостиные", "Прихожие"; bottom modest link "+ Категория". Clear hierarchy.
Main table columns "Работа", "Подкатегория", "Видимость", "Действия". Four spacious rows, each has a beautiful small realistic kitchen thumbnail, title and supporting material:
"Кухня «Гранат»" / "Эмаль, камень" / "Угловые" / green status pill "На сайте" / pencil icon;
"Кухня «Тёплый дуб»" / "МДФ, шпон" / "Угловые" / green "На сайте" / pencil icon;
"Кухня «Шалфей»" / "Эмаль" / "Угловые" / green "На сайте" / pencil icon;
"Кухня «Лён»" / "МДФ" / "Угловые" / grey "Скрыта" / pencil icon.
Use muted small menu dots beside edit pencils.
Below table within page add a restrained split content area: section title "Редактирование работы" with selected item "Кухня «Гранат»"; miniature landscape red kitchen image left and controls right: field label "Название" populated "Кухня «Гранат»", label "Подкатегория" dropdown "Кухни / Угловые", checkbox "Показывать на сайте", buttons green "Сохранить" and ghost "Отмена". Keep this clearly aligned and not cluttered.
Tiny bottom label "Демонстрационные данные".
Constraints: staff roles only administrator and manager. Do not add finance, production/warehouse, charts, extensive settings or designer/master roles. Employee management available as sidebar route but current screen focuses catalog. Consistent crisp buildable desktop UI, accurate Russian text.
```


