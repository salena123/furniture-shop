import { useState, useRef, useEffect } from 'react';
export function CategoryBranch({ category, categories, onNavigate, ancestors = [] }) {
  const [expanded, setExpanded] = useState(false);
  const timer = useRef(null);
  const children = categories.filter(
    (item) => item.parent_id === category.id && !ancestors.includes(item.id),
  );
  useEffect(() => () => clearTimeout(timer.current), []);
  if (!children.length)
    return (
      <a className="category-button" href={`#/catalog/${category.id}`} onClick={onNavigate}>
        {category.name}
      </a>
    );
  return (
    <div
      onMouseEnter={() => {
        timer.current = setTimeout(() => setExpanded(true), 200);
      }}
      onMouseLeave={() => clearTimeout(timer.current)}
    >
      <button
        className="category-button"
        aria-expanded={expanded}
        aria-controls={`children-${category.id}`}
        onClick={() => {
          clearTimeout(timer.current);
          setExpanded((value) => !value);
        }}
      >
        {category.name}
      </button>
      {expanded && (
        <div className="subcategory-list" id={`children-${category.id}`}>
          <a href={`#/catalog/${category.id}`} onClick={onNavigate}>
            Смотреть категорию →
          </a>
          {children.map((child) => (
            <CategoryBranch
              key={child.id}
              category={child}
              categories={categories}
              onNavigate={onNavigate}
              ancestors={[...ancestors, category.id]}
            />
          ))}
        </div>
      )}
    </div>
  );
}
