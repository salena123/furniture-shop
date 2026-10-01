import { useState } from 'react';
import { fieldsFor } from '../../config/adminFields';
import { useResource } from '../../hooks/useResource';
import { useAction } from '../../hooks/useAction';
import { api } from '../../services/api';
import { productDetails } from '../../utils/productDetails';
import { Modal } from '../common/Modal';
import { RecordForm } from '../common/RecordForm';
import { LoadState, ErrorNotice } from '../common/Feedback';
import { ProductAttributes } from './ProductAttributes';
import { ProductImages } from './ProductImages';

const characteristicFields = new Set(['material_id', 'article', 'dimensions', 'color']);

export function ProductEditor({ item, references, user, onClose, onChanged }) {
  const [created, setCreated] = useState(null);
  const [fieldReferences] = useState(references);
  const [section, setSection] = useState('main');
  const [notice, setNotice] = useState('');
  const id = item.id || created?.id;
  const resource = useResource(id ? `/api/products/${id}?include_inactive=true` : null, {
    auth: true,
  });
  const options = useResource('/api/catalog/options');
  const action = useAction();
  const data = resource.data || created || (!id ? item : null);
  const product = data && { ...data, attributes: data.attributes || [], images: data.images || [] };
  const fields = fieldsFor('products', product || {}, fieldReferences, user);
  const changed = () => {
    resource.reload();
    onChanged();
    setNotice('Изменения сохранены');
  };
  const save = (body) =>
    action.run(
      () => api(`/api/products/${id || ''}`, { method: id ? 'PATCH' : 'POST', body, auth: true }),
      (result) => {
        if (!id) {
          setCreated(result);
          setSection('details');
        }
        changed();
      },
    );
  const mutate = (path, method, body, done) =>
    action.run(
      () => api(path, { method, body, auth: true }),
      () => {
        changed();
        done?.();
      },
    );

  return (
    <Modal
      title={id ? 'Изменить товар' : 'Добавить товар'}
      onClose={onClose}
      busy={action.busy}
      wide
    >
      <div className="product-editor-sections" role="group" aria-label="Разделы товара">
        {[
          ['main', 'Основное'],
          ['details', 'Характеристики'],
          ['photos', 'Фотографии'],
        ].map(([key, label]) => (
          <button
            type="button"
            key={key}
            className="button secondary"
            aria-pressed={section === key}
            disabled={action.busy || (!id && key !== 'main')}
            onClick={() => {
              setSection(key);
              action.clearError();
              setNotice('');
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="muted">
        {id
          ? 'Каждый раздел сохраняется отдельно. Добавление и удаление фото и дополнительных значений применяется сразу.'
          : 'Сначала сохраните основные данные товара. Затем можно заполнить характеристики и загрузить фотографии.'}
      </p>
      <LoadState resource={resource} />
      <ErrorNotice message={action.error} />
      {notice && (
        <p className="notice success-notice" role="status">
          {notice}
        </p>
      )}
      {product && (
        <>
          <section hidden={section !== 'main'} aria-label="Основные данные товара">
            <RecordForm
              key={`main-${id || 'new'}`}
              initial={product}
              fields={fields.filter((field) => !characteristicFields.has(field.name))}
              action={action}
              showError={false}
              onSave={save}
              onClose={onClose}
              closeLabel="Закрыть"
              submitLabel={id ? 'Сохранить основные данные' : 'Создать товар'}
            />
          </section>
          {id && (
            <>
              <section hidden={section !== 'details'} aria-label="Характеристики товара">
                <h3>Основные характеристики</h3>
                <p className="muted">
                  Материал используется в фильтре каталога. Другие варианты материала и цвета можно
                  добавить ниже.
                </p>
                <RecordForm
                  key={`details-${id}`}
                  initial={product}
                  fields={fields.filter((field) => characteristicFields.has(field.name))}
                  action={action}
                  showError={false}
                  onSave={save}
                  onClose={onClose}
                  closeLabel="Закрыть"
                  submitLabel="Сохранить характеристики"
                />
                <ProductAttributes
                  resource={{ ...resource, data: product }}
                  action={action}
                  mutate={mutate}
                  item={product}
                  options={options}
                />
                <h3>Как характеристики выглядят на сайте</h3>
                <p className="muted">Здесь показаны сохранённые значения.</p>
                <dl className="details-list">
                  {productDetails(product).map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{value}</dd>
                    </div>
                  ))}
                </dl>
              </section>
              <section hidden={section !== 'photos'} aria-label="Фотографии товара">
                <ProductImages
                  resource={{ ...resource, data: product }}
                  action={action}
                  mutate={mutate}
                  item={product}
                />
              </section>
            </>
          )}
        </>
      )}
    </Modal>
  );
}
