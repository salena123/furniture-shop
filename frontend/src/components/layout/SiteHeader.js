export function SiteHeader({ user }) {
  return (
    <header className="site-header">
      <a className="wordmark" href="#/" aria-label="Маэстро — главная">
        <img className="main-logo" src="/main-logo2.svg" alt="На главную"></img>
      </a>
      <p className="brand-description">
        Изготовление качественной и<br />
        функциональной мебели
      </p>
      <nav className="header-links" aria-label="Основная навигация">
        <a href="#/contacts" className="header-link">
          Контакты
        </a>
        <a href="#/about" className="header-link">
          О нас
        </a>
      </nav>
      <a className="login-button" href={user ? '#/staff' : '#/login'}>
        {user ? 'Кабинет' : 'Войти'}
      </a>
    </header>
  );
}
