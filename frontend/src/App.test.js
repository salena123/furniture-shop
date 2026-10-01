import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import App from './App';
const categories = [
  {
    id: 1,
    name: 'Кухни',
    parent_id: null,
    slug: 'kuhni',
    is_active: true,
  },
  {
    id: 2,
    name: 'Угловые кухни',
    parent_id: 1,
    slug: 'uglovye',
    is_active: true,
  },
  {
    id: 3,
    name: 'Шкафы',
    parent_id: null,
    slug: 'shkafy',
    is_active: true,
  },
  {
    id: 4,
    name: 'Шкафы-купе',
    parent_id: 3,
    slug: 'kupe',
    is_active: true,
  },
];
const product = {
  id: 8,
  category_id: 2,
  product_name: 'Угловая кухня',
  price: 'По запросу',
  is_custom: true,
  material_id: 1,
  material_name: 'МДФ',
  images: [],
  attributes: [],
};
const manager = {
  id: 2,
  name: 'Мария',
  login: 'manager',
  role: 'manager',
};
const admin = {
  id: 1,
  name: 'Администратор',
  login: 'admin',
  role: 'admin',
};
const request = {
  id: 15,
  client_name: 'Анна',
  phone: '+79001234567',
  product_name: 'Кухня',
  status: 'new',
  created_at: '2026-09-25T10:00:00',
  comments: [],
  events: [],
  assigned_manager_id: null,
};
const paged = (items) => ({
  items,
  total: items.length,
  limit: 100,
  offset: 0,
});
const response = (data, status = 200) => ({
  ok: status < 400,
  status,
  json: async () => data,
});
let currentUser;
let loggedIn;
let savedRequest;
let handler;
let liveCategories;
beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute('open', '');
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute('open');
  };
  window.scrollTo = jest.fn();
});
beforeEach(() => {
  window.history.replaceState(null, '', '/');
  sessionStorage.clear();
  currentUser = manager;
  loggedIn = false;
  savedRequest = {
    ...request,
  };
  liveCategories = [...categories];
  handler = null;
  global.fetch = jest.fn(async (url, options = {}) => {
    const parsed = new URL(url);
    if (handler) {
      const result = handler(parsed, options);
      if (result) return result;
    }
    const path = parsed.pathname;
    if (path === '/api/catalog/options')
      return response({
        categories: liveCategories,
        materials: [
          {
            id: 1,
            name: 'МДФ',
          },
        ],
        attributes: [],
      });
    if (path === '/api/auth/me')
      return loggedIn ? response(currentUser) : response({ detail: 'Нужна авторизация' }, 401);
    if (path === '/api/auth/login') {
      loggedIn = true;
      return response({ user: currentUser });
    }
    if (path === '/api/auth/logout') {
      loggedIn = false;
      return response(null, 204);
    }
    if (path === '/api/dashboard/stats')
      return response({
        new_requests: 1,
        assigned_to_me: 0,
        unassigned_requests: 1,
        completed_requests: 0,
      });
    if (path === '/api/requests/') return response(paged([savedRequest]));
    if (path === '/api/requests/15/details') return response(savedRequest);
    if (path === '/api/users/managers') return response([manager, admin]);
    if (path === '/api/products/') return response(paged([product]));
    if (path === '/api/products/8') return response(product);
    if (path === '/api/categories/') return response(paged(liveCategories));
    if (path === '/api/materials/')
      return response(
        paged([
          {
            id: 1,
            name: 'МДФ',
          },
        ]),
      );
    throw new Error(`Unexpected endpoint: ${path}`);
  });
});
afterEach(() => jest.useRealTimers());
const navigate = (route) =>
  act(() => {
    window.history.replaceState(null, '', route);
    window.dispatchEvent(new HashChangeEvent('hashchange'));
  });
const signIn = (route, user = manager) => {
  currentUser = user;
  loggedIn = true;
  window.history.replaceState(null, '', route);
};
test('API categories open inside catalog, expand, and restore focus on Escape', async () => {
  render(<App />);
  const trigger = screen.getByRole('button', {
    name: /Каталог/,
  });
  fireEvent.click(trigger);
  fireEvent.click(
    await screen.findByRole('button', {
      name: /^Шкафы$/,
    }),
  );
  expect(
    screen.getByRole('link', {
      name: 'Шкафы-купе',
    }),
  ).toHaveAttribute('href', '#/catalog/4');
  fireEvent.keyDown(document, {
    key: 'Escape',
  });
  expect(trigger).toHaveAttribute('aria-expanded', 'false');
  expect(trigger).toHaveFocus();
});
test('hover expands nested categories', async () => {
  render(<App />);
  fireEvent.click(
    screen.getByRole('button', {
      name: /Каталог/,
    }),
  );
  const category = await screen.findByRole('button', {
    name: /^Кухни$/,
  });
  jest.useFakeTimers();
  fireEvent.mouseEnter(category);
  act(() => jest.advanceTimersByTime(210));
  expect(
    screen.getByRole('link', {
      name: 'Угловые кухни',
    }),
  ).toBeVisible();
});
test('category navigation sends the category filter and renders real product cards', async () => {
  window.history.replaceState(null, '', '#/catalog/2');
  render(<App />);
  expect(
    await screen.findByRole('heading', {
      name: 'Угловая кухня',
    }),
  ).toBeVisible();
  expect(
    screen.getByRole('heading', {
      level: 1,
    }),
  ).toHaveTextContent('Угловые кухни');
  expect(
    global.fetch.mock.calls.some(([url]) => new URL(url).searchParams.get('category_id') === '2'),
  ).toBe(true);
  fireEvent.change(screen.getByLabelText('Поиск по каталогу'), {
    target: {
      value: 'эмаль',
    },
  });
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Найти',
    }),
  );
  await waitFor(() =>
    expect(
      global.fetch.mock.calls.some(([url]) => new URL(url).searchParams.get('search') === 'эмаль'),
    ).toBe(true),
  );
});
test('carousel wraps after exactly five reference slides', async () => {
  render(<App />);
  await act(async () => {});
  const carousel = screen.getByRole('region', {
    name: 'Карусель кухонь',
  });
  const expected = [
    'Кухня под ваш размер и стиль',
    'Место для тёплых встреч',
    'От идеи до вашей кухни',
    'Ваш стиль в каждой детали',
    'Всё на своём месте',
  ];
  expected.forEach((title, index) => {
    expect(
      within(carousel).getByRole('heading', {
        level: 1,
      }),
    ).toHaveTextContent(title);
    expect(within(carousel).getByRole('img')).toHaveAttribute(
      'alt',
      `Фотография кухни ${index + 1}`,
    );
    fireEvent.click(
      screen.getByRole('button', {
        name: 'Следующий слайд',
      }),
    );
  });
  expect(within(carousel).getByRole('heading')).toHaveTextContent(expected[0]);
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Предыдущий слайд',
    }),
  );
  expect(within(carousel).getByRole('img')).toHaveAttribute('alt', 'Фотография кухни 5');
  const dots = within(carousel).getByRole('group', {
    name: 'Выбор слайда',
  });
  expect(within(dots).getAllByRole('button')).toHaveLength(5);
  fireEvent.click(
    within(dots).getByRole('button', {
      name: 'Слайд 3: От идеи до вашей кухни',
    }),
  );
  expect(within(carousel).getByRole('heading')).toHaveTextContent(expected[2]);
  expect(
    within(dots).getByRole('button', {
      name: 'Слайд 3: От идеи до вашей кухни',
    }),
  ).toHaveAttribute('aria-pressed', 'true');
});
test('inquiry reports failure without clearing fields, then shows server-confirmed success', async () => {
  let fail = true;
  handler = (url, options) =>
    url.pathname === '/api/requests/' && options.method === 'POST'
      ? response(
          fail
            ? {
                detail: 'Не удалось сохранить заявку',
              }
            : {
                ...request,
                ...JSON.parse(options.body),
              },
          fail ? 500 : 200,
        )
      : null;
  render(<App />);
  await act(async () => {});
  fireEvent.click(
    within(
      screen.getByRole('region', {
        name: 'Карусель кухонь',
      }),
    ).getByRole('button', {
      name: 'Оставить заявку',
    }),
  );
  fireEvent.change(screen.getByLabelText(/Ваше имя/), {
    target: {
      value: 'Анна',
    },
  });
  fireEvent.change(screen.getByLabelText(/Телефон/), {
    target: {
      value: '+79001234567',
    },
  });
  fireEvent.change(screen.getByLabelText(/Какая мебель нужна/), {
    target: {
      value: 'Кухня',
    },
  });
  fireEvent.click(screen.getByLabelText(/Согласен на обработку/));
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Отправить заявку',
    }),
  );
  expect(await screen.findByRole('alert')).toHaveTextContent('Не удалось сохранить заявку');
  expect(screen.getByLabelText(/Ваше имя/)).toHaveValue('Анна');
  expect(screen.queryByText('Заявка отправлена')).not.toBeInTheDocument();
  fail = false;
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Отправить заявку',
    }),
  );
  expect(
    await screen.findByRole('heading', {
      name: 'Заявка отправлена',
    }),
  ).toBeVisible();
  const payload = JSON.parse(
    global.fetch.mock.calls.find(
      ([url, opts]) => url.endsWith('/api/requests/') && opts.method === 'POST',
    )[1].body,
  );
  expect(payload).toMatchObject({
    client_name: 'Анна',
    needs_measurements: true,
    personal_data_consent: true,
    product_id: null,
  });
});
test('product inquiry keeps its product reference', async () => {
  window.history.replaceState(null, '', '#/product/8');
  render(<App />);
  fireEvent.click(
    await screen.findByRole('button', {
      name: 'Обсудить проект',
    }),
  );
  expect(screen.getByText('Проект: Угловая кухня')).toBeInTheDocument();
  expect(screen.queryByLabelText(/Какая мебель нужна/)).not.toBeInTheDocument();
  expect(screen.getByLabelText('Материал')).toHaveValue('1');
});
test('login uses API, restores session, and restricts manager navigation', async () => {
  window.history.replaceState(null, '', '#/login');
  render(<App />);
  await waitFor(() => expect(screen.getByLabelText(/Логин/)).toBeEnabled());
  fireEvent.change(screen.getByLabelText(/Логин/), {
    target: {
      value: 'manager',
    },
  });
  fireEvent.change(screen.getByLabelText(/Пароль/), {
    target: {
      value: 'manager12345',
    },
  });
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Войти',
    }),
  );
  await waitFor(() => expect(loggedIn).toBe(true));
  expect(sessionStorage.getItem('maestro.staff.token')).toBeNull();
  navigate('#/staff');
  expect(
    await screen.findByRole('heading', {
      name: 'Здравствуйте, Мария',
    }),
  ).toBeVisible();
  const sidebar = screen.getByRole('navigation', {
    name: 'Личный кабинет',
  });
  expect(
    within(sidebar).queryByRole('link', {
      name: /Сотрудники/,
    }),
  ).not.toBeInTheDocument();
  navigate('#/staff/users');
  expect(await screen.findByText('Раздел недоступен')).toBeVisible();
});
test('request status and comments are saved to API and reflected in detail', async () => {
  signIn('#/staff/requests/15');
  handler = (url, options) => {
    if (url.pathname === '/api/requests/15/status') {
      savedRequest = {
        ...savedRequest,
        ...JSON.parse(options.body),
      };
      return response(savedRequest);
    }
    if (url.pathname === '/api/requests/15/comments' && options.method === 'POST') {
      savedRequest = {
        ...savedRequest,
        comments: [
          {
            id: 1,
            user_id: 2,
            user_name: 'Мария',
            comment_text: JSON.parse(options.body).comment_text,
            created_at: request.created_at,
          },
        ],
      };
      return response(savedRequest.comments[0]);
    }
    return null;
  };
  render(<App />);
  await screen.findByRole('heading', {
    name: 'Заявка №15',
  });
  fireEvent.change(screen.getByLabelText('Статус заявки'), {
    target: {
      value: 'contacted',
    },
  });
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Сохранить статус',
    }),
  );
  await screen.findByText('Изменения сохранены');
  await waitFor(() =>
    expect(
      screen.getByRole('button', {
        name: 'Сохранить статус',
      }),
    ).toBeEnabled(),
  );
  expect(screen.getByLabelText('Статус заявки')).toHaveValue('contacted');
  fireEvent.change(screen.getByLabelText(/Новый комментарий/), {
    target: {
      value: 'Позвонить завтра',
    },
  });
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Добавить комментарий',
    }),
  );
  expect(await screen.findByText('Позвонить завтра')).toBeVisible();
});
test('admin can add a category and it appears in the public menu', async () => {
  signIn('#/staff/categories', admin);
  handler = (url, options) => {
    if (url.pathname === '/api/categories/' && options.method === 'POST') {
      const item = {
        ...JSON.parse(options.body),
        id: 9,
      };
      liveCategories.push(item);
      return response(item);
    }
    return null;
  };
  render(<App />);
  await waitFor(() =>
    expect(
      screen.getByRole('button', {
        name: '+ Добавить категорию',
      }),
    ).toBeEnabled(),
  );
  fireEvent.click(
    screen.getByRole('button', {
      name: '+ Добавить категорию',
    }),
  );
  fireEvent.change(screen.getByLabelText(/^Название/), {
    target: {
      value: 'Гостиные',
    },
  });
  fireEvent.blur(screen.getByLabelText(/^Название/));
  expect(screen.getByLabelText(/Адрес страницы/)).toHaveValue('gostinye');
  fireEvent.click(
    screen.getByRole('button', {
      name: 'Сохранить',
    }),
  );
  await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  navigate('#/');
  fireEvent.click(
    screen.getByRole('button', {
      name: /Каталог/,
    }),
  );
  expect(
    await screen.findByRole('link', {
      name: 'Гостиные',
    }),
  ).toHaveAttribute('href', '#/catalog/9');
});
test('expired session clears token and protects staff pages', async () => {
  signIn('#/staff');
  handler = (url) =>
    url.pathname === '/api/auth/me'
      ? response(
          {
            detail: 'Истёк токен',
          },
          401,
        )
      : null;
  render(<App />);
  expect(
    await screen.findByRole('heading', {
      name: 'Вход для сотрудников',
    }),
  ).toBeVisible();
  expect(sessionStorage.getItem('maestro.staff.token')).toBeNull();
  expect(
    screen.queryByRole('navigation', {
      name: 'Личный кабинет',
    }),
  ).not.toBeInTheDocument();
});
test('catalog URL restores filters and page after a product visit and remount', async () => {
  const catalogRoute = '#/catalog/1?search=%D0%BA%D1%83%D1%85%D0%BD%D1%8F&material_id=1&page=2';
  handler = (url) =>
    url.pathname === '/api/products/'
      ? response({
          items: [product],
          total: 25,
          limit: 12,
          offset: 12,
        })
      : null;
  window.history.replaceState(null, '', catalogRoute);
  const view = render(<App />);
  const card = await screen.findByRole('link', {
    name: /Угловая кухня/,
  });
  expect(screen.getByLabelText('Поиск по каталогу')).toHaveValue('кухня');
  expect(screen.getByLabelText('Материал')).toHaveValue('1');
  expect(
    screen.getByRole('navigation', {
      name: 'Страницы',
    }),
  ).toHaveTextContent('2 / 3');
  expect(
    global.fetch.mock.calls.some(([url]) => {
      const params = new URL(url).searchParams;
      return params.get('include_descendants') === 'true' && params.get('offset') === '12';
    }),
  ).toBe(true);
  navigate(card.getAttribute('href'));
  const back = await screen.findByRole('link', {
    name: '← Вернуться к работам',
  });
  expect(back).toHaveAttribute('href', catalogRoute);
  navigate(back.getAttribute('href'));
  await screen.findByRole('link', {
    name: /Угловая кухня/,
  });
  view.unmount();
  render(<App />);
  await screen.findByRole('link', {
    name: /Угловая кухня/,
  });
  expect(screen.getByLabelText('Поиск по каталогу')).toHaveValue('кухня');
  expect(
    screen.getByRole('navigation', {
      name: 'Страницы',
    }),
  ).toHaveTextContent('2 / 3');
});
test('a catalog page beyond the last page returns to the available results', async () => {
  window.history.replaceState(null, '', '#/catalog?page=99');
  render(<App />);
  await waitFor(() => expect(window.location.hash).toBe('#/catalog'));
  expect(
    await screen.findByRole('link', {
      name: /Угловая кухня/,
    }),
  ).toBeVisible();
});
test('unavailable category and product offer a working route back to the catalog', async () => {
  window.history.replaceState(null, '', '#/catalog/999');
  handler = (url) =>
    url.pathname === '/api/products/999'
      ? response(
          {
            detail: 'Товар не найден',
          },
          404,
        )
      : null;
  render(<App />);
  expect(
    await screen.findByRole('heading', {
      name: 'Раздел недоступен',
    }),
  ).toBeVisible();
  expect(
    screen.getByRole('link', {
      name: 'Перейти в каталог',
    }),
  ).toHaveAttribute('href', '#/catalog');
  navigate('#/product/999');
  expect(
    await screen.findByRole('heading', {
      name: 'Проект недоступен',
    }),
  ).toBeVisible();
  expect(
    screen.queryByRole('button', {
      name: 'Обсудить проект',
    }),
  ).not.toBeInTheDocument();
});
test('home loads a three-item selection from the catalog and both inquiry buttons work', async () => {
  render(<App />);
  const works = screen.getByRole('region', {
    name: 'Наши работы',
  });
  expect(
    await within(works).findByRole('link', {
      name: /Угловая кухня/,
    }),
  ).toHaveAttribute('href', '#/product/8');
  expect(
    within(works).getByRole('link', {
      name: /Смотреть все/,
    }),
  ).toHaveAttribute('href', '#/catalog');
  expect(
    global.fetch.mock.calls.some(
      ([url]) =>
        new URL(url).pathname === '/api/products/' &&
        new URL(url).searchParams.get('limit') === '3',
    ),
  ).toBe(true);
  const process = screen.getByRole('region', {
    name: 'Начнём с ваших пожеланий',
  });
  expect(within(process).getAllByRole('listitem')).toHaveLength(3);
  fireEvent.click(
    within(process).getByRole('button', {
      name: 'Оставить заявку',
    }),
  );
  expect(
    screen.getByRole('dialog', {
      name: 'Давайте обсудим вашу мебель',
    }),
  ).toBeVisible();
});
test('home keeps the carousel and inquiry available when catalog loading fails', async () => {
  handler = (url) =>
    url.pathname === '/api/products/'
      ? response(
          {
            detail: 'Каталог временно недоступен',
          },
          503,
        )
      : null;
  render(<App />);
  const works = screen.getByRole('region', {
    name: 'Наши работы',
  });
  expect(await within(works).findByRole('alert')).toHaveTextContent('Каталог временно недоступен');
  expect(
    screen.getByRole('region', {
      name: 'Карусель кухонь',
    }),
  ).toBeVisible();
  handler = (url) => (url.pathname === '/api/products/' ? response(paged([])) : null);
  fireEvent.click(
    within(works).getByRole('button', {
      name: 'Повторить',
    }),
  );
  expect(await within(works).findByText('Скоро здесь появятся наши работы')).toBeVisible();
  expect(
    within(works).getByRole('button', {
      name: 'Обсудить проект',
    }),
  ).toBeEnabled();
});
