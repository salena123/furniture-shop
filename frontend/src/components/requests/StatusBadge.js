import { STATUS_LABELS } from '../../config/requestStatus';
export const StatusBadge = ({ status }) => (
  <span className={`status-badge status-${status}`}>{STATUS_LABELS[status] || status}</span>
);
