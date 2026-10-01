export function StaffSidebar({ user, nav, section, logout }) {
  return (
    <aside className="staff-sidebar">
      <div className="staff-identity">
        <span className="avatar">{user.name.charAt(0)}</span>
        <div>
          <strong>{user.name}</strong>
          <small>{user.role === 'admin' ? 'Администратор' : 'Менеджер'}</small>
        </div>
      </div>
      <nav aria-label="Личный кабинет">
        {nav.map(([key, label]) => (
          <a
            className={section === key ? 'active' : ''}
            aria-current={section === key ? 'page' : undefined}
            href={key === 'overview' ? '#/staff' : `#/staff/${key}`}
            key={key}
          >
            {label}
            <span aria-hidden="true">{section === key ? '›' : ''}</span>
          </a>
        ))}
      </nav>
      <button
        className="text-button logout-button"
        onClick={async () => {
          if (await logout()) window.location.hash = '#/';
        }}
      >
        Выйти из кабинета
      </button>
    </aside>
  );
}
