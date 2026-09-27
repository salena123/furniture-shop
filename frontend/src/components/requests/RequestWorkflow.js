import { Field } from '../common/Field';
import { STATUS_LABELS } from '../../config/requestStatus';
import { LoadState } from '../common/Feedback';
export function RequestWorkflow({ request, mutate, id, action, user, managers }) {
  return (
    <section className="soft-panel">
      <h2>Работа с заявкой</h2>
      <form
        key={`status-${request.status}`}
        onSubmit={(event) => {
          event.preventDefault();
          mutate(`/api/requests/${id}/status`, 'PATCH', {
            status: new FormData(event.currentTarget).get('status'),
          });
        }}
      >
        <Field
          label="Статус заявки"
          name="status"
          type="select"
          defaultValue={request.status}
          options={Object.entries(STATUS_LABELS).map(([value, label]) => ({
            value,
            label,
          }))}
        />
        <button className="button primary" disabled={action.busy}>
          Сохранить статус
        </button>
      </form>
      <div className="assignment">
        <p className="muted">Ответственный</p>
        <strong>{request.assigned_manager_name || 'Не назначен'}</strong>
        {user.role === 'admin' ? (
          <>
            <LoadState resource={managers} />
            {managers.data && (
              <form
                key={`manager-${request.assigned_manager_id}`}
                onSubmit={(event) => {
                  event.preventDefault();
                  const value = new FormData(event.currentTarget).get('manager');
                  mutate(`/api/requests/${id}/manager`, 'PATCH', {
                    assigned_manager_id: value ? Number(value) : null,
                  });
                }}
              >
                <Field
                  label="Назначить сотрудника"
                  name="manager"
                  type="select"
                  defaultValue={request.assigned_manager_id || ''}
                  options={[
                    {
                      value: '',
                      label: 'Без ответственного',
                    },
                    ...managers.data.map((item) => ({
                      value: item.id,
                      label: item.name,
                    })),
                  ]}
                />
                <button className="button secondary" disabled={action.busy}>
                  Сохранить назначение
                </button>
              </form>
            )}
          </>
        ) : (
          <div className="form-actions">
            {!request.assigned_manager_id && (
              <button
                className="button secondary"
                disabled={action.busy}
                onClick={() => mutate(`/api/requests/${id}/take`, 'PATCH')}
              >
                Взять в работу
              </button>
            )}
            {request.assigned_manager_id === user.id && (
              <button
                className="text-button"
                disabled={action.busy}
                onClick={() =>
                  mutate(`/api/requests/${id}/manager`, 'PATCH', {
                    assigned_manager_id: null,
                  })
                }
              >
                Снять с себя
              </button>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
