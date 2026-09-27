import { useState, useRef, useEffect } from 'react';
import { LoadState } from '../common/Feedback';
import { CategoryBranch } from './CategoryBranch';
export default function CatalogMenu({ resource, route }) {
  const [open, setOpen] = useState(false);
  const panel = useRef(null);
  const trigger = useRef(null);
  const categories = resource.data?.categories || [];
  useEffect(() => {
    setOpen(false);
  }, [route]);
  useEffect(() => {
    if (!open) return;
    const outside = (event) => {
      if (!panel.current?.contains(event.target)) setOpen(false);
    };
    const escape = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
        trigger.current?.focus();
      }
    };
    document.addEventListener('pointerdown', outside);
    document.addEventListener('keydown', escape);
    return () => {
      document.removeEventListener('pointerdown', outside);
      document.removeEventListener('keydown', escape);
    };
  }, [open]);
  return (
    <div className="catalog-slot">
      <div
        ref={panel}
        className={`catalog-panel ${open ? 'is-open' : ''}`}
        onBlur={(event) => {
          if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
        }}
      >
        <button
          ref={trigger}
          className="catalog-trigger"
          aria-expanded={open}
          aria-controls="catalog-items"
          onClick={() => setOpen((value) => !value)}
        >
          <span aria-hidden="true">☰</span> Каталог
        </button>
        {open && (
          <nav id="catalog-items" className="catalog-items" aria-label="Категории товаров">
            <a
              className="category-button all-categories"
              href="#/catalog"
              onClick={() => setOpen(false)}
            >
              Все работы
            </a>
            <LoadState resource={resource} />
            {categories
              .filter((item) => !categories.some((parent) => parent.id === item.parent_id))
              .map((category) => (
                <CategoryBranch
                  key={category.id}
                  category={category}
                  categories={categories}
                  onNavigate={() => setOpen(false)}
                />
              ))}
            {resource.data && !categories.length && (
              <p className="muted">Категории скоро появятся.</p>
            )}
          </nav>
        )}
      </div>
    </div>
  );
}
