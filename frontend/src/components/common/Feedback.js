export function ErrorNotice({ message, onRetry }) {
  if (!message) return null;
  return (
    <div className="notice error-notice" role="alert">
      <span>{message}</span>
      {onRetry && (
        <button className="text-button" onClick={onRetry}>
          Повторить
        </button>
      )}
    </div>
  );
}
export function LoadState({ resource }) {
  return resource.loading ? (
    <div className="loading-state" role="status">
      Загрузка…
    </div>
  ) : (
    <ErrorNotice message={resource.error} onRetry={resource.reload} />
  );
}
export function EmptyState({ title, children }) {
  return (
    <div className="empty-state">
      <span className="empty-mark" aria-hidden="true">
        ◇
      </span>
      <h3>{title}</h3>
      {children}
    </div>
  );
}
