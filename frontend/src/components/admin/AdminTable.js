import { dateTime } from '../../utils/dateTime';
import { api } from '../../services/api';
export function AdminTable({ section, rows, titleOf, references, open, action, saved, user }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>{section === 'users' ? 'Сотрудник' : 'Название'}</th>
            <th>
              {section === 'users' ? 'Роль' : section === 'materials' ? 'Описание' : 'Сведения'}
            </th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.id}>
              <td>
                <strong>{titleOf(item)}</strong>
                <small>{section === 'users' ? item.login : item.slug || `№${item.id}`}</small>
              </td>
              <td>
                {section === 'products' && (
                  <>
                    <span>{item.price}</span>
                    <small>
                      {
                        references.data?.categories.find(
                          (category) => category.id === item.category_id,
                        )?.name
                      }
                    </small>
                  </>
                )}
                {section === 'categories' && (
                  <small>
                    {item.parent_id
                      ? `В категории: ${references.data?.categories.find((category) => category.id === item.parent_id)?.name || item.parent_id}`
                      : 'Основная категория'}{' '}
                    · порядок {item.sort_order}
                  </small>
                )}
                {section === 'materials' && (
                  <span className="table-description">{item.description || '—'}</span>
                )}
                {section === 'users' && (
                  <>
                    {item.role === 'admin' ? 'Администратор' : 'Менеджер'}
                    <small>{item.email || 'Почта не указана'}</small>
                    <small>Вход: {dateTime(item.last_login_at)}</small>
                  </>
                )}
                {'is_active' in item && (
                  <span
                    className={`status-badge ${item.is_active ? 'status-completed' : 'status-cancelled'}`}
                  >
                    {item.is_active ? 'На сайте' : 'Скрыто'}
                  </span>
                )}
              </td>
              <td>
                <div className="table-actions">
                  <button
                    className="text-button"
                    disabled={['products', 'categories'].includes(section) && !references.data}
                    onClick={() =>
                      open({
                        type: 'edit',
                        item,
                      })
                    }
                  >
                    Изменить
                  </button>
                  {section === 'attributes' && (
                    <button
                      className="text-button"
                      onClick={() =>
                        open({
                          type: 'values',
                          item,
                        })
                      }
                    >
                      Значения
                    </button>
                  )}
                  {section === 'products' ? (
                    <button
                      className="text-button"
                      disabled={action.busy}
                      onClick={() =>
                        action.run(
                          () =>
                            api(`/api/products/${item.id}`, {
                              method: 'PATCH',
                              auth: true,
                              body: {
                                is_active: !item.is_active,
                              },
                            }),
                          saved,
                        )
                      }
                    >
                      {item.is_active ? 'Скрыть' : 'Опубликовать'}
                    </button>
                  ) : (
                    <button
                      className="text-button danger-text"
                      disabled={section === 'users' && item.id === user.id}
                      onClick={() =>
                        open({
                          type: 'delete',
                          item,
                        })
                      }
                    >
                      Удалить
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
