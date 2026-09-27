import { useResource } from '../../hooks/useResource';
import { useAuth } from '../../context/AuthContext';
import { PageHeading } from '../../components/common/PageHeading';
import { LoadState, EmptyState } from '../../components/common/Feedback';
import { RequestTable } from '../../components/requests/RequestTable';
export function Dashboard() {
  const stats = useResource('/api/dashboard/stats', {
    auth: true,
  });
  const requests = useResource('/api/requests/?limit=5&offset=0', {
    auth: true,
  });
  const { user } = useAuth();
  return (
    <>
      <PageHeading
        eyebrow={user.role === 'admin' ? 'Кабинет администратора' : 'Кабинет менеджера'}
        title={`Здравствуйте, ${user.name}`}
      >
        Заявки и текущая работа мастерской.
      </PageHeading>
      <LoadState resource={stats} />
      {stats.data && (
        <div className="stats-grid">
          {[
            ['new_requests', 'Новые заявки', '#/staff/requests?status=new'],
            ['assigned_to_me', 'Назначено мне', '#/staff/requests?scope=my'],
            ['unassigned_requests', 'Без ответственного', '#/staff/requests?scope=unassigned'],
            ['completed_requests', 'Завершено', '#/staff/requests?status=completed'],
          ].map(([key, label, href]) => (
            <a className="surface stat-card" href={href} key={key}>
              <span>{label}</span>
              <strong>{stats.data[key]}</strong>
              <small>Открыть заявки ↗</small>
            </a>
          ))}
        </div>
      )}
      <section className="surface">
        <div className="section-top">
          <h2>Последние заявки</h2>
          <a className="text-button" href="#/staff/requests">
            Все заявки →
          </a>
        </div>
        <LoadState resource={requests} />
        {requests.data &&
          (requests.data.items.length ? (
            <RequestTable items={requests.data.items} />
          ) : (
            <EmptyState title="Заявок пока нет">
              <p className="muted">Здесь появятся обращения с сайта.</p>
            </EmptyState>
          ))}
      </section>
    </>
  );
}
