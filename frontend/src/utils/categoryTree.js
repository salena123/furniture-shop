export function descendants(categories, id) {
  const found = new Set([id]);
  let size;
  do {
    size = found.size;
    categories.forEach((category) => {
      if (found.has(category.parent_id)) found.add(category.id);
    });
  } while (size !== found.size);
  return found;
}
