import { StaffSidebar } from '../components/layout/StaffSidebar';
import { useAuth } from '../context/AuthContext';
import { Dashboard } from '../pages/staff/Dashboard';
import { RequestDetail } from '../pages/staff/RequestDetail';
import { RequestsPage } from '../pages/staff/RequestsPage';
import { Profile } from '../pages/staff/Profile';
import AdminPage from '../pages/admin/AdminPage';
import { EmptyState } from '../components/common/Feedback';
export default function StaffPages({ route, onCatalogChanged }) {
  const { user, logout } = useAuth();
  const [path, search = ''] = route.replace('#', '').split('?');
  const segments = path.split('/').filter(Boolean);
  const section = segments[1] || 'overview';
  const nav = [
    ['overview', 'Обзор'],
    ['requests', 'Заявки'],
    ...(user.role === 'admin'
      ? [
          ['products', 'Товары'],
          ['categories', 'Категории'],
          ['materials', 'Материалы'],
          ['attributes', 'Характеристики'],
          ['users', 'Сотрудники'],
        ]
      : []),
    ['profile', 'Мой профиль'],
  ];
  const adminSections = ['products', 'categories', 'materials', 'attributes', 'users'];
  let content;
  if (section === 'overview') content = <Dashboard />;
  else if (section === 'requests')
    content = segments[2] ? (
      <RequestDetail key={segments[2]} id={segments[2]} />
    ) : (
      <RequestsPage key={search} searchParams={new URLSearchParams(search)} />
    );
  else if (section === 'profile') content = <Profile />;
  else if (adminSections.includes(section) && user.role === 'admin')
    content = <AdminPage key={section} section={section} onCatalogChanged={onCatalogChanged} />;
  else
    content = (
      <EmptyState title="Раздел недоступен">
        <a href="#/staff">Вернуться в кабинет</a>
      </EmptyState>
    );
  return (
    <div className="staff-layout">
      <StaffSidebar user={user} nav={nav} section={section} logout={logout} />
      <section className="staff-content" key={section}>
        {content}
      </section>
    </div>
  );
}
