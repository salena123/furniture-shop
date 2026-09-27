import { eventLabel } from '../../utils/requestEvents';
import { dateTime } from '../../utils/dateTime';
export function RequestHistory({ request, managers }) {
  return (
    <section className="surface padded">
      <h2>История заявки</h2>
      {request.events.length ? (
        <ol className="timeline">
          {request.events.map((item) => (
            <li key={item.id}>
              <p>{eventLabel(item, managers.data || [])}</p>
              <small>
                {item.user_name || 'Система'} · {dateTime(item.created_at)}
              </small>
            </li>
          ))}
        </ol>
      ) : (
        <p className="muted">Изменений пока нет.</p>
      )}
    </section>
  );
}
