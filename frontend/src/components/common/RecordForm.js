import { useState } from 'react';
import { Field } from './Field';
import { slugify } from '../../utils/slugify';
import { ErrorNotice } from './Feedback';
export function RecordForm({
  fields,
  initial = {},
  onClose,
  onSave,
  action,
  submitLabel = 'Сохранить',
  closeLabel = 'Отмена',
  showError = true,
}) {
  const [values, setValues] = useState(() =>
    Object.fromEntries(
      fields.map((field) => [
        field.name,
        initial[field.name] ?? field.defaultValue ?? (field.type === 'checkbox' ? false : ''),
      ]),
    ),
  );
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const body = {};
        fields.forEach((field) => {
          const value = values[field.name];
          if (field.type === 'password' && !value && initial.id) return;
          body[field.name] =
            field.type === 'checkbox'
              ? !!value
              : field.number
                ? value === ''
                  ? null
                  : Number(value)
                : typeof value === 'string'
                  ? value.trim() || null
                  : value;
        });
        onSave(body);
      }}
    >
      <fieldset disabled={action.busy}>
        <div className="form-grid">
          {fields.map(
            ({ name, label, type, options, number, defaultValue, hint, wide, ...props }) => (
              <Field
                key={name}
                name={name}
                label={label}
                type={type}
                options={options}
                className={wide || type === 'textarea' ? 'full-width' : ''}
                {...props}
                {...(type === 'checkbox'
                  ? {
                      checked: !!values[name],
                    }
                  : {
                      value: values[name],
                    })}
                onChange={(event) =>
                  setValues((previous) => ({
                    ...previous,
                    [name]: type === 'checkbox' ? event.target.checked : event.target.value,
                  }))
                }
                onBlur={() => {
                  if (
                    (name === 'name' || name === 'product_name') &&
                    'slug' in values &&
                    !values.slug
                  )
                    setValues((previous) => ({
                      ...previous,
                      slug: slugify(previous[name]),
                    }));
                }}
              >
                {hint && <small className="field-hint">{hint}</small>}
              </Field>
            ),
          )}
        </div>
        {showError && <ErrorNotice message={action.error} />}
        <div className="form-actions">
          <button className="button primary" type="submit">
            {action.busy ? 'Сохранение…' : submitLabel}
          </button>
          <button className="button secondary" type="button" onClick={onClose}>
            {closeLabel}
          </button>
        </div>
      </fieldset>
    </form>
  );
}
