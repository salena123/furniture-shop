import { descendants } from '../utils/categoryTree';
export const SLUG = {
  name: 'slug',
  label: 'Адрес страницы',
  required: true,
  pattern: '[a-z0-9]+(?:-[a-z0-9]+)*',
  hint: 'Латиница, цифры и дефисы. Заполняется из названия.',
};
export const SORT = {
  name: 'sort_order',
  label: 'Порядок отображения',
  type: 'number',
  number: true,
  min: 0,
  defaultValue: 0,
  required: true,
};
export const ACTIVE = {
  name: 'is_active',
  label: 'Показывать на сайте',
  type: 'checkbox',
  defaultValue: true,
};
export function fieldsFor(section, initial, references, user) {
  const name = {
    name: 'name',
    label: 'Название',
    required: true,
  };
  const description = {
    name: 'description',
    label: 'Описание',
    type: 'textarea',
  };
  if (section === 'users')
    return [
      {
        name: 'name',
        label: 'Имя сотрудника',
        required: true,
      },
      {
        name: 'login',
        label: 'Логин',
        required: true,
        minLength: 3,
        maxLength: 100,
        pattern: '[A-Za-z0-9_.-]{3,100}',
        hint: 'От 3 символов: латиница, цифры, точка, дефис, подчёркивание.',
        autoComplete: 'off',
      },
      {
        name: 'email',
        label: 'Почта',
        type: 'email',
      },
      {
        name: 'role',
        label: 'Роль',
        type: 'select',
        defaultValue: 'manager',
        disabled: initial.id === user.id,
        options: [
          {
            value: 'manager',
            label: 'Менеджер',
          },
          {
            value: 'admin',
            label: 'Администратор',
          },
        ],
      },
      {
        name: 'password',
        label: initial.id ? 'Новый пароль' : 'Пароль',
        type: 'password',
        required: !initial.id,
        minLength: 8,
        autoComplete: 'new-password',
        hint: initial.id
          ? 'Оставьте пустым, чтобы сохранить текущий пароль.'
          : 'Не менее 8 символов.',
      },
    ];
  if (section === 'materials') return [name, description];
  if (section === 'attributes') return [name, ACTIVE];
  const categories = references?.categories || [];
  if (section === 'categories') {
    const excluded = initial.id ? descendants(categories, initial.id) : new Set();
    return [
      name,
      SLUG,
      {
        name: 'parent_id',
        label: 'Родительская категория',
        type: 'select',
        number: true,
        options: [
          {
            value: '',
            label: 'Нет — основная категория',
          },
          ...categories
            .filter((item) => !excluded.has(item.id))
            .map((item) => ({
              value: item.id,
              label: item.name,
            })),
        ],
      },
      SORT,
      {
        ...ACTIVE,
        wide: true,
        hint: 'Скрытый раздел, его подкатегории и товары не видны посетителям. Настройки публикации вложенных элементов сохраняются.',
      },
      description,
    ];
  }
  return [
    {
      name: 'product_name',
      label: 'Название товара',
      required: true,
    },
    SLUG,
    {
      name: 'category_id',
      label: 'Категория',
      type: 'select',
      number: true,
      required: true,
      options: [
        {
          value: '',
          label: 'Выберите категорию',
        },
        ...categories.map((item) => ({
          value: item.id,
          label: `${item.name}${item.is_active ? '' : ' (скрыта)'}`,
        })),
      ],
    },
    {
      name: 'price',
      label: 'Цена или условия расчёта',
      required: true,
      placeholder: 'Например, от 150 000 ₽',
    },
    {
      name: 'material_id',
      label: 'Материал',
      type: 'select',
      number: true,
      options: [
        {
          value: '',
          label: 'Не выбран',
        },
        ...(references?.materials || []).map((item) => ({
          value: item.id,
          label: item.name,
        })),
      ],
    },
    {
      name: 'article',
      label: 'Артикул',
    },
    {
      name: 'dimensions',
      label: 'Размеры',
    },
    {
      name: 'color',
      label: 'Цвет',
    },
    SORT,
    {
      name: 'is_custom',
      label: 'Изготавливается на заказ',
      type: 'checkbox',
      defaultValue: true,
    },
    ACTIVE,
    {
      name: 'short_description',
      label: 'Краткое описание',
      type: 'textarea',
    },
    description,
    {
      name: 'meta_title',
      label: 'Заголовок для поисковых систем',
    },
    {
      name: 'meta_description',
      label: 'Описание для поисковых систем',
      type: 'textarea',
    },
  ];
}
