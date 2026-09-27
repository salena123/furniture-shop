import { RequestDialogs } from '../../components/requests/RequestDialogs';
import { api } from '../../services/api';
import { RequestHistory } from '../../components/requests/RequestHistory';
import { RequestWorkflow } from '../../components/requests/RequestWorkflow';
import { RequestComments } from '../../components/requests/RequestComments';
import { ClientProject } from '../../components/requests/ClientProject';
import { ErrorNotice, LoadState } from '../../components/common/Feedback';
import { StatusBadge } from '../../components/requests/StatusBadge';
import { dateTime } from '../../utils/dateTime';
import { PageHeading } from '../../components/common/PageHeading';
import { useAuth } from '../../context/AuthContext';
import { useResource } from '../../hooks/useResource';
import { useAction } from '../../hooks/useAction';
import { useState } from 'react';
export function RequestDetail({ id }) {
  const { user } = useAuth();
  const resource = useResource(`/api/requests/${id}/details`, {
    auth: true,
  });
  const managers = useResource('/api/users/managers', {
    auth: true,
  });
  const action = useAction();
  const [modal, setModal] = useState(null);
  const [notice, setNotice] = useState('');
  const request = resource.data;
  const mutate = (path, method, body, after) =>
    action.run(
      () =>
        api(path, {
          method,
          body,
          auth: true,
        }),
      () => {
        setModal(null);
        resource.reload();
        setNotice('Изменения сохранены');
        after?.();
      },
    );
  const openModal = (value) => {
    action.clearError();
    setModal(value);
  };
  return (
    <>
      <a className="back-link" href="#/staff/requests">
        ← Все заявки
      </a>
      <LoadState resource={resource} />
      <>
        {request && (
          <>
            <PageHeading
              eyebrow={`Получена ${dateTime(request.created_at)}`}
              title={`Заявка №${request.id}`}
              action={<StatusBadge status={request.status} />}
            >
              {request.product_name}
            </PageHeading>
            {notice && (
              <p className="notice success-notice" role="status">
                {notice}
              </p>
            )}
            <ErrorNotice message={!modal ? action.error : ''} />
            <div className="request-layout">
              <div className="request-main">
                <ClientProject openModal={openModal} request={request} />
                <RequestComments
                  request={request}
                  user={user}
                  openModal={openModal}
                  mutate={mutate}
                  id={id}
                  busy={action.busy}
                />
              </div>
              <aside className="request-side">
                <RequestWorkflow
                  request={request}
                  mutate={mutate}
                  id={id}
                  action={action}
                  user={user}
                  managers={managers}
                />
                <RequestHistory request={request} managers={managers} />
                {user.role === 'admin' && (
                  <button
                    className="text-button danger-text"
                    onClick={() =>
                      openModal({
                        type: 'delete-request',
                      })
                    }
                  >
                    Удалить заявку
                  </button>
                )}
              </aside>
            </div>
            <RequestDialogs
              modal={modal}
              request={request}
              setModal={setModal}
              action={action}
              mutate={mutate}
              id={id}
            />
          </>
        )}
      </>
    </>
  );
}
