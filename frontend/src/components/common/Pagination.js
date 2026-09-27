export function Pagination({ total, offset, limit, onChange }) {
  if (total <= limit) return null;
  return (
    <nav className="pagination" aria-label="Страницы">
      <button
        className="button secondary"
        disabled={!offset}
        onClick={() => onChange(Math.max(0, offset - limit))}
      >
        ← Назад
      </button>
      <span>
        {Math.floor(offset / limit) + 1} / {Math.ceil(total / limit)}
      </span>
      <button
        className="button secondary"
        disabled={offset + limit >= total}
        onClick={() => onChange(offset + limit)}
      >
        Далее →
      </button>
    </nav>
  );
}
