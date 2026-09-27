import { Field } from '../common/Field';
export function CatalogFilters({ setFilters, filters, search, setSearch, options }) {
  return (
    <form
      className="filter-bar"
      onSubmit={(event) => {
        event.preventDefault();
        setFilters({
          ...filters,
          search: search.trim(),
        });
      }}
    >
      <Field
        label="Поиск по каталогу"
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Название, цвет или материал"
      />
      <Field
        label="Материал"
        type="select"
        value={filters.material_id}
        onChange={(event) =>
          setFilters({
            ...filters,
            material_id: event.target.value,
          })
        }
        options={[
          {
            value: '',
            label: 'Все материалы',
          },
          ...(options.data?.materials || []).map((item) => ({
            value: item.id,
            label: item.name,
          })),
        ]}
      />
      <button className="button primary" type="submit">
        Найти
      </button>
      {(filters.search || filters.material_id) && (
        <button
          className="text-button"
          type="button"
          onClick={() => {
            setFilters({});
            setSearch('');
          }}
        >
          Сбросить
        </button>
      )}
    </form>
  );
}
