export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div>
        <strong>МАЭСТРО</strong>
        <p>Кухни и мебель для вашего дома</p>
      </div>
      <nav aria-label="Навигация в подвале">
        <a href="#/catalog">Каталог</a>
        <a href="#/about">О нас</a>
        <a href="#/contacts">Контакты</a>
      </nav>
      <span>© {new Date().getFullYear()} Маэстро</span>
    </footer>
  );
}
