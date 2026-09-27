import { STATUS_LABELS } from '../config/requestStatus';
export function eventLabel(event, managers = []) {
  if (event.event_type === 'status_changed')
    return `${STATUS_LABELS[event.old_status] || 'Статус'} → ${STATUS_LABELS[event.new_status] || event.new_status}`;
  if (event.event_type === 'comment_added') return 'Добавлен комментарий';
  if (event.event_type === 'manager_assigned') {
    const match = event.message?.match(/^Ответственный изменён с (None|\d+) на (None|\d+)$/);
    if (!match) return 'Изменён ответственный';
    const name = (id) =>
      id === 'None'
        ? 'Не назначен'
        : managers.find((person) => person.id === Number(id))?.name || `Сотрудник №${id}`;
    return `Ответственный: ${name(match[1])} → ${name(match[2])}`;
  }
  return event.message || 'Заявка обновлена';
}
