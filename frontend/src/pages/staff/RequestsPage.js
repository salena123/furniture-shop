import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useResource } from '../../hooks/useResource';
import { query } from '../../services/api';
import { PageHeading } from '../../components/common/PageHeading';
import { Field } from '../../components/common/Field';
import { STATUS_LABELS } from '../../config/requestStatus';
import { LoadState, EmptyState } from '../../components/common/Feedback';
import { RequestTable } from '../../components/requests/RequestTable';
import { Pagination } from '../../components/common/Pagination';
export function RequestsPage({ searchParams }) {
  const [filter, setFilter] = useState({
    search: '',
    status: searchParams.get('status') || '',
    scope: searchParams.get('scope') || '',
  });
  const [search, setSearch] = useState('');
  const [offset, setOffset] = useState(0);
  const { user } = useAuth();
  const resource = useResource(
    query('/api/requests/', {
      search: filter.search,
      status: filter.status,
      assigned_manager_id: filter.scope === 'my' ? user.id : null,
      unassigned_only: filter.scope === 'unassigned',
      limit: 15,
      offset,
    }),
    {
      auth: true,
    },
  );
  const change = (key, value) => {
    setFilter((previous) => ({
      ...previous,
      [key]: value,
    }));
    setOffset(0);
  };
  return (
    <>
      <PageHeading
        title="Заявки клиентов"
        action={
          <button className="button secondary" onClick={resource.reload}>
            Обновить
          </button>
        }
      >
        От первого обращения до согласованного проекта.
      </PageHeading>
      <form
        className="filter-bar"
        onSubmit={(event) => {
          event.preventDefault();
          change('search', search.trim());
        }}
      >
        <Field
          label="Поиск"
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Имя, телефон или проект"
        />
        <Field
          label="Статус"
          type="select"
          value={filter.status}
          onChange={(event) => change('status', event.target.value)}
          options={[
            {
              value: '',
              label: 'Все статусы',
            },
            ...Object.entries(STATUS_LABELS).map(([value, label]) => ({
              value,
              label,
            })),
          ]}
        />
        <Field
          label="Ответственный"
          type="select"
          value={filter.scope}
          onChange={(event) => change('scope', event.target.value)}
          options={[
            {
              value: '',
              label: 'Все заявки',
            },
            {
              value: 'my',
              label: 'Назначено мне',
            },
            {
              value: 'unassigned',
              label: 'Без ответственного',
            },
          ]}
        />
        <button className="button primary">Найти</button>
      </form>
      <LoadState resource={resource} />
      {resource.data && (
        <>
          <p className="result-count">Заявок: {resource.data.total}</p>
          <div className="surface">
            {resource.data.items.length ? (
              <RequestTable items={resource.data.items} />
            ) : (
              <EmptyState title="Заявок не найдено">
                <p className="muted">Измените фильтры или дождитесь новых обращений.</p>
              </EmptyState>
            )}
          </div>
          <Pagination total={resource.data.total} offset={offset} limit={15} onChange={setOffset} />
        </>
      )}
    </>
  );
}
