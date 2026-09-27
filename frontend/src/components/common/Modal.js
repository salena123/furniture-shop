import { useRef, useId, useEffect } from 'react';
export function Modal({ title, children, onClose, busy = false, wide = false }) {
  const ref = useRef(null);
  const id = useId();
  useEffect(() => {
    const previousFocus = document.activeElement;
    const element = ref.current;
    element.showModal();
    return () => {
      element.close();
      previousFocus?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={wide ? 'wide-dialog' : ''}
      aria-labelledby={id}
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) onClose();
      }}
    >
      <button className="dialog-close" aria-label="Закрыть окно" disabled={busy} onClick={onClose}>
        ×
      </button>
      <h2 id={id}>{title}</h2>
      {children}
    </dialog>
  );
}
