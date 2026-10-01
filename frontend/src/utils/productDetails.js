export function normalizeDetail(value) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .toLocaleLowerCase('ru');
}

export function detailKey(name) {
  const key = normalizeDetail(name);
  return { материалы: 'материал', цвета: 'цвет', размер: 'размеры' }[key] || key;
}

// Объединяем старые поля и справочные характеристики без потери значений.
export function productDetails(product) {
  if (!product) return [];
  const groups = new Map();
  const rows = [
    ['Артикул', product.article],
    ['Материал', product.material_name || product.material],
    ['Цвет', product.color],
    ['Размеры', product.dimensions],
    ...(product.attributes || []).map((attribute) => [attribute.attribute_name, attribute.value]),
  ];
  for (const [name, rawValue] of rows) {
    if (!name || !rawValue?.trim()) continue;
    const key = detailKey(name);
    const group = groups.get(key) || { label: name.trim(), values: [] };
    if (!group.values.some((value) => normalizeDetail(value) === normalizeDetail(rawValue))) {
      group.values.push(rawValue.trim());
    }
    groups.set(key, group);
  }
  return [...groups].map(([key, group]) => [
    group.values.length > 1 && key === 'цвет'
      ? 'Доступные цвета'
      : group.values.length > 1 && key === 'материал'
        ? 'Доступные материалы'
        : group.label,
    group.values.join(', '),
  ]);
}
