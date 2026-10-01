import { useState } from 'react';
import { Field } from '../common/Field';
import { ProductImage } from '../common/ProductImage';
export function ProductImages({ resource, mutate, action, item }) {
  const [remove, setRemove] = useState(null);

  return (
    <>
      <h3 className="section-heading">Фотографии</h3>
      <p className="muted">
        Главная фотография отображается в каталоге. Остальные доступны в галерее товара.
      </p>
      <div className="value-list">
        {resource.data.images.map((image) => (
          <form
            className="image-editor"
            key={`${image.id}-${image.is_main}-${image.sort_order}`}
            onSubmit={(event) => {
              event.preventDefault();
              const values = Object.fromEntries(new FormData(event.currentTarget));
              mutate(`/api/products/images/${image.id}`, 'PUT', {
                image_url: image.image_url,
                alt_text: values.alt_text || null,
                sort_order: Number(values.sort_order),
                is_main: values.is_main === 'on',
              });
            }}
          >
            <p className="file-label">
              Фотография №{image.id}{' '}
              {image.is_main && <span className="status-badge">Главная</span>}
            </p>
            <ProductImage
              image={image}
              alt={`${item.product_name}: фотография №${image.id}`}
              className="admin-photo"
            />
            <fieldset disabled={action.busy}>
              <div className="form-grid">
                <Field
                  label="Описание фотографии"
                  name="alt_text"
                  defaultValue={image.alt_text || ''}
                />
                <Field
                  label="Порядок"
                  name="sort_order"
                  type="number"
                  min="0"
                  required
                  defaultValue={image.sort_order}
                />
                <Field
                  label="Главная фотография"
                  name="is_main"
                  type="checkbox"
                  defaultChecked={image.is_main}
                />
              </div>
              <div className="inline-actions">
                <button className="text-button">Сохранить</button>
                <button
                  type="button"
                  className="text-button danger-text"
                  onClick={() => setRemove(image)}
                >
                  Удалить
                </button>
              </div>
            </fieldset>
          </form>
        ))}
      </div>
      {remove && (
        <div className="notice inline-confirm">
          <p>Удалить фотографию №{remove.id}?</p>
          <button
            className="button danger"
            disabled={action.busy}
            onClick={() =>
              mutate(`/api/products/images/${remove.id}`, 'DELETE', undefined, () =>
                setRemove(null),
              )
            }
          >
            Удалить
          </button>
          <button className="text-button" onClick={() => setRemove(null)}>
            Отмена
          </button>
        </div>
      )}
      <form
        className="upload-form"
        onSubmit={(event) => {
          event.preventDefault();
          const form = event.currentTarget;
          mutate(`/api/products/${item.id}/images/upload`, 'POST', new FormData(form), () =>
            form.reset(),
          );
        }}
      >
        <fieldset disabled={action.busy}>
          <Field
            label="Загрузить фотографию"
            type="file"
            name="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            required
          />
          <Field label="Описание" name="alt_text" />
          <button className="button secondary">{action.busy ? 'Сохранение…' : 'Загрузить'}</button>
        </fieldset>
      </form>
    </>
  );
}
