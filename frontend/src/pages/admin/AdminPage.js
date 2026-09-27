import { AdminTable } from '../../components/admin/AdminTable';
import { useAuth } from '../../context/AuthContext';
import { useState } from 'react';
import { useAction } from '../../hooks/useAction';
import { useLists } from '../../hooks/useLists';
import { useReferences } from '../../hooks/useReferences';
import { useResource } from '../../hooks/useResource';
import { query, api } from '../../services/api';
import { PageHeading } from '../../components/common/PageHeading';
import { TITLES, SINGULAR } from '../../config/adminSections';
import { LoadState, EmptyState, ErrorNotice } from '../../components/common/Feedback';
import { Field } from '../../components/common/Field';
import { Pagination } from '../../components/common/Pagination';
import RecordEditor from '../../components/common/RecordEditor';
import { fieldsFor } from '../../config/adminFields';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import { AttributeValues } from '../../components/admin/AttributeValues';
import { ProductExtras } from '../../components/admin/ProductExtras';
export default function AdminPage({ section, onCatalogChanged }) {
  const { user, refresh } = useAuth();
  const [revision, setRevision] = useState(0);
  const [modal, setModal] = useState(null);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('');
  const [offset, setOffset] = useState(0);
  const [notice, setNotice] = useState('');
  const action = useAction();
  const list = useLists(section, revision);
  const references = useReferences(revision, ['products', 'categories'].includes(section));
  const products = useResource(
    section === 'products'
      ? query('/api/products/', {
          include_inactive: true,
          search: filter,
          limit: 15,
          offset,
        })
      : null,
    {
      auth: true,
      version: revision,
    },
  );
  const reload = () => setRevision((value) => value + 1);
  const resource =
    section === 'products'
      ? products
      : {
          ...list,
          reload,
        };
  const filtered =
    section === 'products'
      ? []
      : (list.data || []).filter((item) =>
          [item.name, item.login, item.description, item.email]
            .filter(Boolean)
            .join(' ')
            .toLowerCase()
            .includes(filter.toLowerCase()),
        );
  const rows =
    section === 'products' ? products.data?.items || [] : filtered.slice(offset, offset + 15);
  const total = section === 'products' ? products.data?.total || 0 : filtered.length;
  const changed = () => {
    reload();
    onCatalogChanged();
  };
  const open = (value) => {
    action.clearError();
    setModal(value);
  };
  const saved = (result) => {
    setModal(null);
    changed();
    setNotice('Изменения сохранены');
    if (section === 'users' && result?.id === user.id) refresh();
  };
  const titleOf = (item) => item.product_name || item.name;
  return (
    <>
      <PageHeading
        title={TITLES[section]}
        action={
          <button
            className="button primary"
            disabled={['products', 'categories'].includes(section) && !references.data}
            onClick={() =>
              open({
                type: 'edit',
                item: {},
              })
            }
          >
            + Добавить {SINGULAR[section]}
          </button>
        }
      >
        {section === 'categories'
          ? 'Создавайте категории и подкатегории — меню сайта обновится автоматически.'
          : section === 'users'
            ? 'Доступ менеджеров и администраторов.'
            : 'Содержимое каталога мастерской.'}
      </PageHeading>
      {['products', 'categories'].includes(section) && (
        <LoadState
          resource={{
            ...references,
            reload,
          }}
        />
      )}
      {notice && (
        <p className="notice success-notice" role="status">
          {notice}
        </p>
      )}
      <form
        className="filter-bar"
        onSubmit={(event) => {
          event.preventDefault();
          setFilter(search.trim());
          setOffset(0);
        }}
      >
        <Field
          label="Поиск"
          type="search"
          placeholder="Название или имя"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <button className="button primary">Найти</button>
        <button
          type="button"
          className="text-button"
          onClick={() => {
            setSearch('');
            setFilter('');
            setOffset(0);
            reload();
          }}
        >
          Обновить
        </button>
      </form>
      <LoadState resource={resource} />
      {resource.data && (
        <>
          <p className="result-count">Всего: {total}</p>
          <div className="surface">
            {rows.length ? (
              <AdminTable
                section={section}
                rows={rows}
                titleOf={titleOf}
                references={references}
                open={open}
                action={action}
                saved={saved}
                user={user}
              />
            ) : (
              <EmptyState title="Записей пока нет">
                <p className="muted">Добавьте новую запись или измените поиск.</p>
              </EmptyState>
            )}
          </div>
          <Pagination total={total} offset={offset} limit={15} onChange={setOffset} />
        </>
      )}
      {!modal && <ErrorNotice message={action.error} />}
      {modal?.type === 'edit' && (
        <RecordEditor
          title={`${modal.item.id ? 'Изменить' : 'Добавить'} ${SINGULAR[section]}`}
          initial={modal.item}
          fields={fieldsFor(section, modal.item, references.data, user)}
          onClose={() => setModal(null)}
          action={action}
          onSave={(body) =>
            action.run(
              () =>
                api(`/api/${section}/${modal.item.id || ''}`, {
                  method: modal.item.id ? 'PATCH' : 'POST',
                  body,
                  auth: true,
                }),
              saved,
            )
          }
        />
      )}
      {modal?.type === 'delete' && (
        <ConfirmDialog
          title={`Удалить ${SINGULAR[section]}?`}
          action={action}
          onClose={() => setModal(null)}
          onConfirm={() =>
            action.run(
              () =>
                api(`/api/${section}/${modal.item.id}`, {
                  method: 'DELETE',
                  auth: true,
                }),
              () => {
                setOffset(0);
                saved();
              },
            )
          }
        >
          «{titleOf(modal.item)}» будет удалён.{' '}
          {section === 'materials'
            ? 'Связанные товары и заявки останутся, но материал будет отвязан.'
            : 'Действие нельзя отменить. Записи с зависимостями могут быть защищены от удаления.'}
        </ConfirmDialog>
      )}
      {modal?.type === 'values' && (
        <AttributeValues item={modal.item} onClose={() => setModal(null)} onChanged={changed} />
      )}
      {modal?.type === 'extras' && (
        <ProductExtras item={modal.item} onClose={() => setModal(null)} onChanged={changed} />
      )}
    </>
  );
}
