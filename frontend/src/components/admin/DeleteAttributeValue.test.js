import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { DeleteAttributeValue } from './DeleteAttributeValue';
import { useAction } from '../../hooks/useAction';

function Confirmation(props) {
  return <DeleteAttributeValue value={{ id: 5, value: 'Венге' }} action={useAction()} {...props} />;
}
let count;
let failUsage;
let failDelete;
beforeEach(() => {
  count = 3;
  failUsage = false;
  failDelete = false;
  global.fetch = jest.fn(async (url, options = {}) => {
    const failure = options.method === 'DELETE' ? failDelete : failUsage;
    return {
      ok: !failure,
      status: failure ? 400 : 200,
      json: async () =>
        failure
          ? { detail: 'Не удалось выполнить действие' }
          : { id: 5, value: 'Венге', products_count: count },
    };
  });
});
afterEach(() => {
  delete global.fetch;
});

test('shows affected product count and sends forced deletion only after confirmation', async () => {
  const onDeleted = jest.fn();
  render(<Confirmation onDeleted={onDeleted} onCancel={jest.fn()} />);
  expect(screen.getByRole('button', { name: 'Удалить', exact: true })).toBeDisabled();
  const confirm = await screen.findByRole('button', { name: 'Удалить у всех товаров' });
  expect(screen.getByText(/Используется у товаров: 3/)).toBeInTheDocument();
  expect(global.fetch.mock.calls.some(([, options]) => options.method === 'DELETE')).toBe(false);
  fireEvent.click(confirm);
  await waitFor(() => expect(onDeleted).toHaveBeenCalledTimes(1));
  expect(global.fetch).toHaveBeenCalledWith(
    expect.stringContaining('/values/5?force=true'),
    expect.objectContaining({ method: 'DELETE' }),
  );
});

test('cancel makes no delete request', async () => {
  const onCancel = jest.fn();
  render(<Confirmation onDeleted={jest.fn()} onCancel={onCancel} />);
  await screen.findByText(/Используется у товаров: 3/);
  fireEvent.click(screen.getByRole('button', { name: 'Отмена' }));
  expect(onCancel).toHaveBeenCalledTimes(1);
  expect(global.fetch.mock.calls.some(([, options]) => options.method === 'DELETE')).toBe(false);
});

test('unused value is deleted normally; a new dependency requires another confirmation', async () => {
  count = 0;
  const onDeleted = jest.fn();
  render(<Confirmation onDeleted={onDeleted} onCancel={jest.fn()} />);
  await screen.findByText(/Значение не используется/);
  count = 1;
  failDelete = true;
  fireEvent.click(screen.getByRole('button', { name: 'Удалить', exact: true }));
  await screen.findByRole('button', { name: 'Удалить у всех товаров' });
  expect(onDeleted).not.toHaveBeenCalled();
  expect(global.fetch).toHaveBeenCalledWith(
    expect.stringMatching(/\/values\/5$/),
    expect.objectContaining({ method: 'DELETE' }),
  );
  failDelete = false;
  fireEvent.click(screen.getByRole('button', { name: 'Удалить у всех товаров' }));
  await waitFor(() => expect(onDeleted).toHaveBeenCalledTimes(1));
});

test('usage load failure prevents destructive action and permits retry', async () => {
  failUsage = true;
  render(<Confirmation onDeleted={jest.fn()} onCancel={jest.fn()} />);
  await screen.findByText('Не удалось выполнить действие');
  expect(screen.getByRole('button', { name: 'Удалить', exact: true })).toBeDisabled();
  failUsage = false;
  fireEvent.click(screen.getByRole('button', { name: /Повторить/ }));
  await screen.findByRole('button', { name: 'Удалить у всех товаров' });
});
