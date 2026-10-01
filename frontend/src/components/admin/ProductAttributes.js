import { LoadState } from '../common/Feedback';
import { Field } from '../common/Field';
import { detailKey, normalizeDetail } from '../../utils/productDetails';
export function ProductAttributes({ resource, action, mutate, item, options }) {
  const groups = new Map();
  resource.data.attributes.forEach((attribute) => {
    const key = detailKey(attribute.attribute_name);
    if (!groups.has(key)) groups.set(key, { name: attribute.attribute_name, values: [] });
    groups.get(key).values.push(attribute);
  });
  return (
    <>
      <h3>Дополнительные характеристики и варианты</h3>
      <p className="muted">
        Добавьте стиль, тип изделия или другие варианты материала и цвета. На сайте значения одной
        характеристики объединяются в одну строку.
      </p>
      <div className="value-list">
        {[...groups].map(([key, group]) => (
          <div className="product-attribute-group" key={key}>
            <strong>{group.name}</strong>
            <div className="product-attribute-values">
              {group.values.map((attribute) => (
                <span className="product-attribute-value" key={attribute.id}>
                  {attribute.value}
                  <button
                    type="button"
                    className="text-button danger-text"
                    disabled={action.busy}
                    aria-label={`Убрать ${group.name}: ${attribute.value}`}
                    onClick={() =>
                      mutate(`/api/products/${item.id}/attributes/${attribute.id}`, 'DELETE')
                    }
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      <LoadState resource={options} />
      {options.data && (
        <form
          className="inline-form"
          onSubmit={(event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const value = new FormData(form).get('attribute');
            mutate(`/api/products/${item.id}/attributes/${value}`, 'POST', undefined, () =>
              form.reset(),
            );
          }}
        >
          <Field
            label="Добавить характеристику"
            name="attribute"
            type="select"
            required
            options={[
              {
                value: '',
                label: 'Выберите значение',
              },
              ...options.data.attributes.flatMap((attribute) =>
                attribute.values
                  .filter(
                    (value) =>
                      !resource.data.attributes.some(
                        (existing) =>
                          existing.id === value.id ||
                          (detailKey(existing.attribute_name) === detailKey(attribute.name) &&
                            normalizeDetail(existing.value) === normalizeDetail(value.value)),
                      ) &&
                      ![
                        ['Материал', resource.data.material_name || resource.data.material],
                        ['Цвет', resource.data.color],
                        ['Размеры', resource.data.dimensions],
                        ['Артикул', resource.data.article],
                      ].some(
                        ([name, current]) =>
                          detailKey(name) === detailKey(attribute.name) &&
                          normalizeDetail(current) === normalizeDetail(value.value),
                      ),
                  )
                  .map((value) => ({
                    value: value.id,
                    label: `${attribute.name}: ${value.value}`,
                  })),
              ),
            ]}
          />
          <button className="button secondary" disabled={action.busy}>
            Добавить
          </button>
        </form>
      )}
    </>
  );
}
