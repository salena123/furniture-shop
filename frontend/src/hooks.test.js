import { act, renderHook, waitFor } from '@testing-library/react';
import { useAction } from './hooks/useAction';
import { useResource } from './hooks/useResource';
test('simultaneous submits share one in-flight action, then allow another attempt', async () => {
  let complete;
  const task = jest.fn(
    () =>
      new Promise((resolve) => {
        complete = resolve;
      }),
  );
  const { result } = renderHook(() => useAction());
  let pending;
  act(() => {
    pending = result.current.run(task);
    result.current.run(task);
  });
  expect(task).toHaveBeenCalledTimes(1);
  expect(result.current.busy).toBe(true);
  await act(async () => {
    complete();
    await pending;
  });
  expect(result.current.busy).toBe(false);
  await act(async () =>
    result.current.run(async () => {
      throw new Error('Попробуйте снова');
    }),
  );
  expect(result.current.error).toBe('Попробуйте снова');
  await act(async () => result.current.run(async () => 'ok'));
  expect(result.current.error).toBe('');
});
test('refresh retains content, but a changed resource does not expose stale data', async () => {
  let finish;
  global.fetch = jest
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        name: 'Первый',
      }),
    })
    .mockImplementation(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
  const { result, rerender } = renderHook(({ path }) => useResource(path), {
    initialProps: {
      path: '/api/products/1',
    },
  });
  await waitFor(() => expect(result.current.data?.name).toBe('Первый'));
  act(() => result.current.reload());
  expect(result.current.loading).toBe(true);
  expect(result.current.data.name).toBe('Первый');
  await act(async () =>
    finish({
      ok: true,
      json: async () => ({
        name: 'Обновлённый',
      }),
    }),
  );
  expect(result.current.data.name).toBe('Обновлённый');
  rerender({
    path: '/api/products/2',
  });
  expect(result.current.data).toBeNull();
  await act(async () =>
    finish({
      ok: false,
      status: 404,
      json: async () => ({
        detail: 'Не найден',
      }),
    }),
  );
  expect(result.current.status).toBe(404);
  expect(result.current.data).toBeNull();
});
