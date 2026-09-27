import { dateTime } from '../../utils/dateTime';
import { StatusBadge } from './StatusBadge';
export function RequestTable({ items }) {
  return (
    <div className="table-scroll">
      <table className="requests-table">
        <thead>
          <tr>
            <th>Заявка</th>
            <th>Клиент</th>
            <th>Проект</th>
            <th>Статус</th>
            <th>Ответственный</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <a className="table-link" href={`#/staff/requests/${item.id}`}>
                  №{item.id} →
                </a>
                <small>{dateTime(item.created_at)}</small>
              </td>
              <td data-label="Клиент">
                <strong>{item.client_name}</strong>
                <small>{item.phone}</small>
              </td>
              <td data-label="Проект">
                {item.product_name}
                <small>{item.city || 'Город не указан'}</small>
              </td>
              <td data-label="Статус">
                <StatusBadge status={item.status} />
              </td>
              <td data-label="Ответственный">
                {item.assigned_manager_name || <span className="muted">Не назначен</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
