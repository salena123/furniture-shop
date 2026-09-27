import { LoadState } from '../common/Feedback';
import { Field } from '../common/Field';
export function ProductAttributes({ resource, action, mutate, item, options }) {
  return (
    <>
      <h3>Характеристики проекта</h3>
      <div className="value-list">
        {resource.data.attributes.map((attribute) => (
          <div className="value-row" key={attribute.id}>
            <span>
              {attribute.attribute_name}: {attribute.value}
            </span>
            <button
              className="text-button danger-text"
              disabled={action.busy}
              onClick={() =>
                mutate(`/api/products/${item.id}/attributes/${attribute.id}`, 'DELETE')
              }
            >
              Убрать
            </button>
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
                      !resource.data.attributes.some((existing) => existing.id === value.id),
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
