import RecordEditor from '../common/RecordEditor';
import { requestFields } from '../../config/requestFields';
import { ConfirmDialog } from '../common/ConfirmDialog';
import { api } from '../../services/api';
export function RequestDialogs({ modal, request, setModal, action, mutate, id }) {
  return (
    <>
      {modal?.type === 'edit' && (
        <RecordEditor
          title="Редактировать заявку"
          initial={request}
          fields={requestFields}
          onClose={() => setModal(null)}
          action={action}
          onSave={(body) => mutate(`/api/requests/${id}`, 'PATCH', body)}
        />
      )}
      {modal?.type === 'comment' && (
        <RecordEditor
          title="Изменить комментарий"
          initial={modal.item}
          fields={[
            {
              name: 'comment_text',
              label: 'Комментарий',
              type: 'textarea',
              required: true,
            },
          ]}
          onClose={() => setModal(null)}
          action={action}
          onSave={(body) => mutate(`/api/requests/${id}/comments/${modal.item.id}`, 'PUT', body)}
        />
      )}
      {modal?.type === 'delete-comment' && (
        <ConfirmDialog
          title="Удалить комментарий?"
          onClose={() => setModal(null)}
          action={action}
          onConfirm={() => mutate(`/api/requests/${id}/comments/${modal.item.id}`, 'DELETE')}
        >
          Комментарий будет удалён из заявки.
        </ConfirmDialog>
      )}
      {modal?.type === 'delete-request' && (
        <ConfirmDialog
          title={`Удалить заявку №${id}?`}
          onClose={() => setModal(null)}
          action={action}
          onConfirm={() =>
            action.run(
              () =>
                api(`/api/requests/${id}`, {
                  method: 'DELETE',
                  auth: true,
                }),
              () => {
                window.location.hash = '#/staff/requests';
              },
            )
          }
        >
          Заявка и связанные комментарии будут удалены. Это действие нельзя отменить.
        </ConfirmDialog>
      )}
    </>
  );
}
