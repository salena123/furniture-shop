import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { ContactsPage } from './ContactsPage';
import { InfoPage } from '../public/InfoPage';
import { contacts, resolveContacts } from '../../config/contacts';

let stored;
let failSave;
beforeEach(() => {
  stored = { configured: true, phone: null, address: null, hours: null, email: null };
  failSave = false;
  global.fetch = jest.fn(async (url, options = {}) => {
    if (options.method === 'PUT') {
      if (failSave)
        return {
          ok: false,
          status: 400,
          json: async () => ({ detail: 'Не удалось сохранить контакты' }),
        };
      stored = { ...JSON.parse(options.body), configured: true };
    }
    return { ok: true, status: 200, json: async () => stored };
  });
});
afterEach(() => {
  delete global.fetch;
});

test('administrator saves contacts and visitors see the same data and links', async () => {
  const editor = render(<ContactsPage />);
  fireEvent.change(await screen.findByLabelText('Телефон'), {
    target: { value: '+7 (900) 123-45-67' },
  });
  fireEvent.change(screen.getByLabelText('Адрес'), { target: { value: 'ул. Мебельная, 1' } });
  fireEvent.change(screen.getByLabelText('Часы работы'), {
    target: { value: 'Пн–Пт: 9–18\nСб: 10–16' },
  });
  fireEvent.change(screen.getByLabelText('Почта'), { target: { value: 'hello@example.com' } });
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить', exact: true }));
  await screen.findByText('Контакты сохранены');
  editor.unmount();
  render(<InfoPage type="contacts" onEnquiry={jest.fn()} />);
  expect(await screen.findByRole('link', { name: '+7 (900) 123-45-67' })).toHaveAttribute(
    'href',
    'tel:+79001234567',
  );
  expect(screen.getByRole('link', { name: 'hello@example.com' })).toHaveAttribute(
    'href',
    'mailto:hello@example.com',
  );
  expect(screen.getByText('ул. Мебельная, 1')).toBeInTheDocument();
  expect(screen.getByText(/Пн–Пт: 9–18/).textContent).toContain('\n');
});

test('failed save retains form values and can be retried', async () => {
  failSave = true;
  render(<ContactsPage />);
  fireEvent.change(await screen.findByLabelText('Адрес'), { target: { value: 'Новый адрес' } });
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить', exact: true }));
  await screen.findByText('Не удалось сохранить контакты');
  expect(screen.getByLabelText('Адрес')).toHaveValue('Новый адрес');
  expect(screen.queryByText('Контакты сохранены')).not.toBeInTheDocument();
  failSave = false;
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить', exact: true }));
  await screen.findByText('Контакты сохранены');
});

test('clearing a saved field shows a placeholder and does not restore old environment settings', async () => {
  expect(resolveContacts({ configured: false })).toBe(contacts);
  expect(resolveContacts(stored).phone).toBeNull();
  stored.phone = '+79001234567';
  const editor = render(<ContactsPage />);
  fireEvent.change(await screen.findByLabelText('Телефон'), { target: { value: '' } });
  fireEvent.click(screen.getByRole('button', { name: 'Сохранить', exact: true }));
  await waitFor(() => expect(stored.phone).toBeNull());
  editor.unmount();
  render(<InfoPage type="contacts" onEnquiry={jest.fn()} />);
  expect(await screen.findAllByText('Информация скоро появится')).toHaveLength(4);
});
