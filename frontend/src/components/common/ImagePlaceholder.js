export function ImagePlaceholder({ label = 'Фотография проекта', className = '' }) {
  return (
    <div className={`image-placeholder ${className}`} role="img" aria-label={label}>
      <svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <rect x="5" y="7" width="38" height="34" rx="3" />
        <circle cx="16" cy="18" r="4" />
        <path d="m6 35 12-12 10 10 6-6 9 9" />
      </svg>
      <span>{label}</span>
    </div>
  );
}
