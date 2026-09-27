import { Modal } from './Modal';
import { ErrorNotice } from './Feedback';
export function ConfirmDialog({ title, children, onConfirm, onClose, action }) {
  return (
    <Modal title={title} onClose={onClose} busy={action.busy}>
      <p className="muted">{children}</p>
      <ErrorNotice message={action.error} />
      <div className="form-actions">
        <button className="button danger" disabled={action.busy} onClick={onConfirm}>
          {action.busy ? 'Удаление…' : 'Удалить'}
        </button>
        <button className="button secondary" disabled={action.busy} onClick={onClose}>
          Отмена
        </button>
      </div>
    </Modal>
  );
}
