export const requestFields = [
  {
    name: 'client_name',
    label: 'Имя клиента',
    required: true,
  },
  {
    name: 'phone',
    label: 'Телефон',
    type: 'tel',
    required: true,
  },
  {
    name: 'product_name',
    label: 'Проект',
    required: true,
  },
  {
    name: 'city',
    label: 'Город',
  },
  {
    name: 'preferred_contact_time',
    label: 'Удобное время связи',
  },
  {
    name: 'color_name',
    label: 'Цвет',
  },
  {
    name: 'dimensions',
    label: 'Размеры',
  },
  {
    name: 'needs_measurements',
    label: 'Нужен замер',
    type: 'checkbox',
  },
  {
    name: 'comment',
    label: 'Пожелания клиента',
    type: 'textarea',
  },
];
