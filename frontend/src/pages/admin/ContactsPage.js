import { useState } from 'react';
import { useResource } from '../../hooks/useResource';
import { useAction } from '../../hooks/useAction';
import { api } from '../../services/api';
import { resolveContacts } from '../../config/contacts';
import { PageHeading } from '../../components/common/PageHeading';
import { LoadState } from '../../components/common/Feedback';
import { RecordForm } from '../../components/common/RecordForm';

const fields = [
  {
    name: 'phone',
    label: 'Телефон',
    type: 'tel',
    maxLength: 50,
    placeholder: '+7 (900) 123-45-67',
  },
  { name: 'email', label: 'Почта', type: 'email', maxLength: 254 },
  { name: 'address', label: 'Адрес', type: 'textarea', maxLength: 500 },
  {
    name: 'hours',
    label: 'Часы работы',
    type: 'textarea',
    maxLength: 300,
    placeholder: 'Пн–Пт: 09:00–18:00\nСб–Вс: выходной',
  },
];

export function ContactsPage() {
  const resource = useResource('/api/site/contacts');
  const action = useAction();
  const [saved, setSaved] = useState(false);
  const save = (body) => {
    setSaved(false);
    action.run(
      () => api('/api/site/contacts', { method: 'PUT', auth: true, body }),
      () => {
        setSaved(true);
        resource.reload();
      },
    );
  };

  return (
    <>
      <PageHeading title="Контакты сайта">
        Изменения появятся на странице «Контакты» после сохранения. Пустое поле отображается как
        «Информация скоро появится».
      </PageHeading>
      <LoadState resource={resource} />
      {saved && (
        <p className="notice success-notice" role="status">
          Контакты сохранены
        </p>
      )}
      {resource.data && (
        <div className="surface padded">
          <RecordForm
            initial={resolveContacts(resource.data)}
            fields={fields}
            action={action}
            onSave={save}
            onClose={() => {
              window.location.hash = '#/contacts';
            }}
            closeLabel="Открыть страницу контактов"
          />
        </div>
      )}
    </>
  );
}
