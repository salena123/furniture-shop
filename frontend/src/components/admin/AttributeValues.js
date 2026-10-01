import { useResource } from '../../hooks/useResource';
import { useAction } from '../../hooks/useAction';
import { useState } from 'react';
import { api } from '../../services/api';
import { Modal } from '../common/Modal';
import { LoadState, ErrorNotice } from '../common/Feedback';
import { Field } from '../common/Field';
import { DeleteAttributeValue } from './DeleteAttributeValue';
export function AttributeValues({ item, onClose, onChanged }) {
  const resource = useResource(`/api/attributes/${item.id}/details?include_inactive=true`, {
    auth: true,
  });
  const action = useAction();
  const [edit, setEdit] = useState(null);
  const [remove, setRemove] = useState(null);
  const save = (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = Object.fromEntries(new FormData(form));
    action.run(
      () =>
        api(edit ? `/api/attributes/values/${edit.id}` : `/api/attributes/${item.id}/values`, {
          method: edit ? 'PATCH' : 'POST',
          auth: true,
          body: {
            value: values.value,
            sort_order: Number(values.sort_order),
          },
        }),
      () => {
        setEdit(null);
        form.reset();
        resource.reload();
        onChanged();
      },
    );
  };
  return (
    <Modal title={`Значения: ${item.name}`} onClose={onClose} busy={action.busy} wide>
      <LoadState resource={resource} />
      {!remove && <ErrorNotice message={action.error} />}
      {resource.data && (
        <>
          <div className="value-list">
            {resource.data.values.map((value) => (
              <div className="value-row" key={value.id}>
                <span>
                  {value.value}
                  <small>Порядок: {value.sort_order}</small>
                </span>
                <div className="inline-actions">
                  <button
                    className="text-button"
                    disabled={action.busy}
                    onClick={() => {
                      action.clearError();
                      setRemove(null);
                      setEdit(value);
                    }}
                  >
                    Изменить
                  </button>
                  <button
                    className="text-button danger-text"
                    disabled={action.busy}
                    onClick={() => {
                      action.clearError();
                      setRemove(value);
                    }}
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
          {!resource.data.values.length && (
            <p className="muted">Добавьте первое значение характеристики.</p>
          )}
        </>
      )}
      {remove && (
        <DeleteAttributeValue
          key={remove.id}
          value={remove}
          action={action}
          onCancel={() => {
            action.clearError();
            setRemove(null);
          }}
          onDeleted={() => {
            setRemove(null);
            if (edit?.id === remove.id) setEdit(null);
            resource.reload();
            onChanged();
          }}
        />
      )}
      <form key={edit?.id || 'new'} onSubmit={save}>
        <h3>{edit ? 'Изменить значение' : 'Новое значение'}</h3>
        <fieldset disabled={action.busy}>
          <div className="form-grid">
            <Field label="Значение" name="value" defaultValue={edit?.value || ''} required />
            <Field
              label="Порядок"
              name="sort_order"
              type="number"
              min="0"
              defaultValue={edit?.sort_order || 0}
              required
            />
          </div>
          <div className="form-actions">
            <button className="button primary">{edit ? 'Сохранить' : 'Добавить'}</button>
            {edit && (
              <button type="button" className="text-button" onClick={() => setEdit(null)}>
                Отмена
              </button>
            )}
          </div>
        </fieldset>
      </form>
    </Modal>
  );
}
