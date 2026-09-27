import { useAuth } from '../../context/AuthContext';
import { PageHeading } from '../../components/common/PageHeading';
import { dateTime } from '../../utils/dateTime';
export function Profile() {
  const { user } = useAuth();
  return (
    <>
      <PageHeading title="Мой профиль">Данные учётной записи сотрудника.</PageHeading>
      <div className="surface padded profile-card">
        <div className="avatar">{user.name.charAt(0)}</div>
        <h2>{user.name}</h2>
        <dl className="details-list">
          {[
            ['Роль', user.role === 'admin' ? 'Администратор' : 'Менеджер'],
            ['Логин', user.login],
            ['Почта', user.email],
            ['Последний вход', dateTime(user.last_login_at)],
          ].map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value || 'Не указано'}</dd>
            </div>
          ))}
        </dl>
        <p className="muted">
          {user.role === 'admin'
            ? 'Изменить данные и пароль можно в разделе «Сотрудники».'
            : 'Для изменения данных или пароля обратитесь к администратору.'}
        </p>
      </div>
    </>
  );
}
