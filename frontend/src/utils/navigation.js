import { query } from '../services/api';
export function catalogLocation(categoryId, filters = {}) {
  return query(categoryId ? `#/catalog/${categoryId}` : '#/catalog', {
    search: filters.search,
    material_id: filters.material_id,
    page: filters.page > 1 ? filters.page : undefined,
  });
}
export function catalogReturnLocation(search) {
  const from = new URLSearchParams(search).get('from');
  return /^#\/catalog(?:\/\d+)?(?:\?[^#]*)?$/.test(from || '') ? from : '#/catalog';
}
export function categoryAncestors(category, categories = []) {
  const result = [];
  const visited = new Set([category?.id]);
  let parent = categories.find((item) => item.id === category?.parent_id);
  while (parent && !visited.has(parent.id)) {
    visited.add(parent.id);
    result.unshift({
      label: parent.name,
      href: `#/catalog/${parent.id}`,
    });
    const parentId = parent.parent_id;
    parent = categories.find((item) => item.id === parentId);
  }
  return result;
}
