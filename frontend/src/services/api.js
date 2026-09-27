export const API_BASE = (process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000').replace(
  /\/$/,
  '',
);
export const TOKEN_KEY = 'maestro.staff.token';
export const session = {
  get: () => sessionStorage.getItem(TOKEN_KEY),
  set: (token) =>
    token ? sessionStorage.setItem(TOKEN_KEY, token) : sessionStorage.removeItem(TOKEN_KEY),
};
export function query(path, params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined && value !== false)
      search.set(key, value);
  });
  const suffix = search.toString();
  return `${path}${suffix ? `?${suffix}` : ''}`;
}
export async function api(path, { body, auth = false, headers, ...options } = {}) {
  let response;
  const token = auth && session.get();
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...(body !== undefined && !(body instanceof FormData)
          ? {
              'Content-Type': 'application/json',
            }
          : {}),
        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),
        ...headers,
      },
      ...(body !== undefined
        ? {
            body: body instanceof FormData ? body : JSON.stringify(body),
          }
        : {}),
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Не удалось связаться с сервером. Проверьте соединение и попробуйте ещё раз.');
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && auth) window.dispatchEvent(new Event('maestro:session-expired'));
    const detail = data?.detail;
    const message =
      response.status === 401 && auth
        ? 'Сессия завершилась. Войдите снова.'
        : typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((item) => item.msg.replace(/^Value error, /, '')).join('. ')
            : data?.message || 'Не удалось выполнить действие. Попробуйте ещё раз.';
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
}
export async function allPages(path, options = {}) {
  const items = [];
  for (let offset = 0; ; offset += 100) {
    const data = await api(
      `${path}${path.includes('?') ? '&' : '?'}limit=100&offset=${offset}`,
      options,
    );
    items.push(...data.items);
    if (items.length >= data.total || !data.items.length) return items;
  }
}
