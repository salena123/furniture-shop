export function Breadcrumbs({ items = [] }) {
  return (
    <nav className="breadcrumbs" aria-label="Хлебные крошки">
      <a href="#/">Главная</a>
      {items.map((item, i) => (
        <span key={i}>
          <span aria-hidden="true">/</span>
          {item.href ? (
            <a href={item.href}>{item.label}</a>
          ) : (
            <span aria-current="page">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
