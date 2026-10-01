import { useRef } from 'react';

export function AboutTextEditor({ value, onChange, id }) {
  const input = useRef(null);
  function format(before, after = '', placeholder = 'Текст') {
    const field = input.current;
    const start = field.selectionStart;
    const end = field.selectionEnd;
    const selection = value.slice(start, end) || placeholder;
    const prefix = before.endsWith(' ') && start > 0 && value[start - 1] !== '\n' ? '\n' : '';
    const inserted = prefix + before + selection + after;
    onChange(value.slice(0, start) + inserted + value.slice(end));
    requestAnimationFrame(() => {
      field.focus();
      field.setSelectionRange(
        start + prefix.length + before.length,
        start + prefix.length + before.length + selection.length,
      );
    });
  }
  return (
    <div>
      <label htmlFor={id}>Текст блока</label>
      <div className="about-toolbar" role="group" aria-label="Форматирование текста">
        <button type="button" onClick={() => format('## ', '', 'Заголовок')}>
          Заголовок
        </button>
        <button type="button" onClick={() => format('**', '**')}>
          Жирный
        </button>
        <button type="button" onClick={() => format('*', '*')}>
          Курсив
        </button>
        <button type="button" onClick={() => format('- ', '', 'Пункт списка')}>
          Список
        </button>
        <button type="button" onClick={() => format('1. ', '', 'Пункт списка')}>
          Нумерация
        </button>
        <button
          type="button"
          onClick={() => format('[', '](https://example.com)', 'Название ссылки')}
        >
          Ссылка
        </button>
      </div>
      <textarea
        id={id}
        ref={input}
        rows={8}
        maxLength={20000}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <small className="muted">
        Выделите текст и нажмите кнопку. Форматирование обозначается символами; результат виден в
        предпросмотре. В ссылке замените https://example.com на свой адрес.
      </small>
    </div>
  );
}
