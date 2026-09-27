import { CatalogFilters } from '../../components/catalog/CatalogFilters';
import { useState, useEffect } from 'react';
import { catalogLocation, categoryAncestors } from '../../utils/navigation';
import { useResource } from '../../hooks/useResource';
import { query } from '../../services/api';
import { LoadState, EmptyState } from '../../components/common/Feedback';
import { UnavailablePage } from '../../components/common/UnavailablePage';
import { Breadcrumbs } from '../../components/common/Breadcrumbs';
import { PageHeading } from '../../components/common/PageHeading';
import { ProductCard } from '../../components/catalog/ProductCard';
import { Pagination } from '../../components/common/Pagination';
export function CatalogPage({ categoryId, searchParams = '', options }) {
  const params = new URLSearchParams(searchParams);
  const filters = {
    search: params.get('search') || '',
    material_id: /^\d+$/.test(params.get('material_id') || '') ? params.get('material_id') : '',
  };
  const requestedPage = Number(params.get('page') || 1);
  const page =
    Number.isSafeInteger(requestedPage) &&
    requestedPage > 0 &&
    Number.isSafeInteger(requestedPage * 12)
      ? requestedPage
      : 1;
  const offset = (page - 1) * 12;
  const [search, setSearch] = useState(filters.search);
  useEffect(() => setSearch(filters.search), [filters.search]);
  const setFilters = (next) => {
    window.location.hash = catalogLocation(categoryId, next);
  };
  const resource = useResource(
    query('/api/products/', {
      category_id: categoryId,
      include_descendants: !!categoryId,
      ...filters,
      limit: 12,
      offset,
    }),
  );
  const lastPage = resource.data ? Math.max(1, Math.ceil(resource.data.total / 12)) : null;
  useEffect(() => {
    if (lastPage !== null && page > lastPage) {
      const location = catalogLocation(categoryId, {
        search: filters.search,
        material_id: filters.material_id,
        page: lastPage,
      });
      window.history.replaceState(null, '', location);
      window.dispatchEvent(new HashChangeEvent('hashchange'));
    }
  }, [lastPage, page, categoryId, filters.search, filters.material_id]);
  const category = options.data?.categories.find((item) => String(item.id) === categoryId);
  const children =
    options.data?.categories.filter(
      (item) => (item.parent_id || null) === (categoryId ? Number(categoryId) : null),
    ) || [];
  const ancestors = categoryAncestors(category, options.data?.categories);
  if (categoryId && !options.data)
    return (
      <section className="content-page">
        <LoadState resource={options} />
      </section>
    );
  if (categoryId && !category)
    return (
      <UnavailablePage
        title="Раздел недоступен"
        description="Возможно, он был скрыт или удалён. Посмотрите другие разделы каталога."
      />
    );
  return (
    <section className="content-page">
      <Breadcrumbs
        items={[
          ...(categoryId
            ? [
                {
                  label: 'Каталог',
                  href: '#/catalog',
                },
              ]
            : []),
          ...ancestors,
          {
            label: category?.name || 'Каталог',
          },
        ]}
      />
      <PageHeading eyebrow="Мебель и наши работы" title={category?.name || 'Каталог'}>
        {category?.description || 'Выберите проект, который подойдёт вашему интерьеру.'}
      </PageHeading>
      <LoadState resource={options} />
      {!!children.length && (
        <nav className="category-chips" aria-label="Подкатегории">
          {children.map((item) => (
            <a className="chip" key={item.id} href={`#/catalog/${item.id}`}>
              {item.name}
              <span aria-hidden="true">↗</span>
            </a>
          ))}
        </nav>
      )}
      <CatalogFilters
        setFilters={setFilters}
        filters={filters}
        search={search}
        setSearch={setSearch}
        options={options}
      />
      <LoadState resource={resource} />
      {resource.data && (
        <>
          <p className="result-count" aria-live="polite">
            Найдено работ: {resource.data.total}
          </p>
          <div className="product-grid" aria-busy={resource.loading}>
            {resource.data.items.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                from={catalogLocation(categoryId, {
                  ...filters,
                  page,
                })}
              />
            ))}
          </div>
          {!resource.data.items.length && (
            <EmptyState title="Работы не найдены">
              <p className="muted">
                {children.length
                  ? 'Выберите подкатегорию выше или измените параметры поиска.'
                  : 'Попробуйте другие параметры или загляните позже.'}
              </p>
            </EmptyState>
          )}
          <Pagination
            total={resource.data.total}
            limit={12}
            offset={offset}
            onChange={(next) =>
              setFilters({
                ...filters,
                page: next / 12 + 1,
              })
            }
          />
        </>
      )}
    </section>
  );
}
