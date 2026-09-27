import { useId } from 'react';
export function Field({ label, type = 'text', options = [], children, className = '', ...props }) {
  const id = useId();
  return (
    <label
      className={`field ${type === 'checkbox' ? 'check-field' : ''} ${className}`}
      htmlFor={id}
    >
      {type === 'checkbox' ? (
        <>
          <input id={id} type="checkbox" {...props} />
          <span>
            {label}
            {children}
          </span>
        </>
      ) : (
        <>
          <span>
            {label}
            {props.required && <span className="required-mark"> *</span>}
          </span>
          {type === 'textarea' ? (
            <textarea id={id} rows="3" {...props} />
          ) : type === 'select' ? (
            <select id={id} {...props}>
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          ) : (
            <input id={id} type={type} {...props} />
          )}
          {children}
        </>
      )}
    </label>
  );
}
