import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { ProductEditor } from './ProductEditor';
import { productDetails } from '../../utils/productDetails';

const references = {
  categories: [{ id: 1, name: 'Стулья', is_active: true }],
  materials: [{ id: 1, name: 'дерево' }],
};
const initial = {
  id: 8,
  product_name: 'Стул',
  slug: 'chair',
  category_id: 1,
  price: '2000 рублей',
  material_id: 1,
  material_name: 'дерево',
  color: 'белый',
  is_custom: true,
  is_active: true,
  images: [],
  attributes: [
    { id: 10, attribute_name: 'материал', value: 'дуб' },
    { id: 11, attribute_name: 'материал', value: 'сосна' },
    { id: 12, attribute_name: 'Цвет', value: 'Графит' },
    { id: 13, attribute_name: 'Стиль', value: 'Классика' },
    { id: 14, attribute_name: 'Цвет', value: 'Венге' },
    { id: 15, attribute_name: ' цвет ', value: ' БЕЛЫЙ ' },
  ],
};
let stored;
beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute('open', '');
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute('open');
  };
});
beforeEach(() => {
  stored = { ...initial };
  global.fetch = jest.fn(async (url, options = {}) => {
    let data;
    const path = new URL(url).pathname;
    if (path === '/api/catalog/options')
      data = {
        attributes: [
          {
            id: 1,
            name: 'Цвет',
            values: [
              { id: 77, value: 'белый' },
              { id: 78, value: 'синий' },
            ],
          },
        ],
      };
    else if (options.method === 'POST') {
      stored = { ...JSON.parse(options.body), id: 9, images: [], attributes: [] };
      data = stored;
    } else if (options.method === 'PATCH') {
      stored = { ...stored, ...JSON.parse(options.body) };
      data = stored;
    } else data = stored;
    return { ok: true, status: 200, json: async () => data };
  });
});
afterEach(() => {
  delete global.fetch;
});

test('merges legacy and additional values once without discarding materials or colors', () => {
  expect(productDetails(initial)).toEqual([
    ['Доступные материалы', 'дерево, дуб, сосна'],
    ['Доступные цвета', 'белый, Графит, Венге'],
    ['Стиль', 'Классика'],
  ]);
  expect(productDetails(null)).toEqual([]);
  expect(productDetails({ attributes: [{ attribute_name: 'Цвет', value: 'Красный' }] })).toEqual([
    ['Цвет', 'Красный'],
  ]);
});

test('keeps draft fields when switching sections and saves only the selected section', async () => {
  render(
    <ProductEditor
      item={initial}
      references={references}
      user={{ role: 'admin' }}
      onClose={jest.fn()}
      onChanged={jest.fn()}
    />,
  );
  const name = await screen.findByLabelText(/Название товара/);
  fireEvent.change(name, { target: { value: 'Новый стул' } });
  fireEvent.click(screen.getByRole('button', { name: 'Характеристики', exact: true }));
  expect(screen.getByText('дерево, дуб, сосна')).toBeInTheDocument();
  expect(screen.getByText('белый, Графит, Венге')).toBeInTheDocument();
  const choices = screen.getByLabelText(/Добавить характеристику/);
  expect(within(choices).queryByRole('option', { name: 'Цвет: белый' })).not.toBeInTheDocument();
  expect(within(choices).getByRole('option', { name: 'Цвет: синий' })).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Цвет', { exact: true }), {
    target: { value: 'кремовый' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить характеристики' }));
  await waitFor(() => expect(stored.color).toBe('кремовый'));
  expect(stored.product_name).toBe('Стул');
  expect(stored.attributes).toEqual(initial.attributes);
  await screen.findByText('кремовый, Графит, Венге, БЕЛЫЙ');
  fireEvent.click(screen.getByRole('button', { name: 'Основное', exact: true }));
  expect(screen.getByLabelText(/Название товара/)).toHaveValue('Новый стул');
  fireEvent.click(screen.getByRole('button', { name: 'Фотографии', exact: true }));
  expect(screen.getByLabelText(/Загрузить фотографию/)).toBeVisible();
});

test('creates the product first and opens characteristics and photographs in the same dialog', async () => {
  render(
    <ProductEditor
      item={{}}
      references={references}
      user={{ role: 'admin' }}
      onClose={jest.fn()}
      onChanged={jest.fn()}
    />,
  );
  expect(screen.getByRole('button', { name: 'Фотографии', exact: true })).toBeDisabled();
  fireEvent.change(screen.getByLabelText(/Название товара/), { target: { value: 'Стол' } });
  fireEvent.blur(screen.getByLabelText(/Название товара/));
  fireEvent.change(screen.getByLabelText(/Категория/), { target: { value: '1' } });
  fireEvent.change(screen.getByLabelText(/Цена или условия расчёта/), {
    target: { value: 'По запросу' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Создать товар' }));
  await screen.findByRole('heading', { name: 'Основные характеристики' });
  expect(screen.getAllByRole('dialog')).toHaveLength(1);
  expect(stored.product_name).toBe('Стол');
  await waitFor(() =>
    expect(screen.getByRole('button', { name: 'Фотографии', exact: true })).toBeEnabled(),
  );
  fireEvent.click(screen.getByRole('button', { name: 'Фотографии', exact: true }));
  expect(screen.getByLabelText(/Загрузить фотографию/)).toBeVisible();
});
