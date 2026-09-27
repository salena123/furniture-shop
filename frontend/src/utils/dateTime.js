export const dateTime = (value) =>
  value
    ? new Intl.DateTimeFormat('ru-RU', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(new Date(/Z$|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`))
    : '—';
