import { API_BASE } from '../services/api';

// Загруженные файлы раздаёт backend, а не сервер React.
export function productImageUrl(value) {
  const url = value?.trim();
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('//') || /^[a-z][a-z\d+.-]*:/i.test(url)) return '';
  return `${API_BASE}/${url.replace(/^\/+/, '')}`;
}

export function sortedProductImages(images = []) {
  return [...images].sort(
    (a, b) =>
      Number(!!b.is_main) - Number(!!a.is_main) ||
      (a.sort_order || 0) - (b.sort_order || 0) ||
      a.id - b.id,
  );
}
