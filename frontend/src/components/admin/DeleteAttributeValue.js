import { useResource } from '../../hooks/useResource';
import { api } from '../../services/api';
import { LoadState, ErrorNotice } from '../common/Feedback';

export function DeleteAttributeValue({ value, action, onCancel, onDeleted }) {
  const usage = useResource(`/api/attributes/values/${value.id}/usage`, { auth: true });
  const inUse = usage.data?.products_count > 0;
  const confirm = () =>
    action.run(async () => {
      try {
        return await api(`/api/attributes/values/${value.id}${inUse ? '?force=true' : ''}`, {
          method: 'DELETE',
          auth: true,
        });
      } catch (error) {
        // A value may have been linked to a product since the preview was loaded.
        usage.reload();
        throw error;
      }
    }, onDeleted);

  return (
    <section className="notice inline-confirm" aria-label="Подтверждение удаления значения">
      <p>Удалить «{usage.data?.value || value.value}»?</p>
      <LoadState resource={usage} />
      <ErrorNotice message={action.error} />
      {usage.data && !usage.error && (
        <p>
          {inUse
            ? `Используется у товаров: ${usage.data.products_count}. Значение будет удалено из справочника и дополнительных характеристик всех этих товаров. Сами товары, фотографии и основные поля товара сохранятся. Отменить действие нельзя.`
            : 'Значение не используется у товаров и будет удалено из справочника. Отменить действие нельзя.'}
        </p>
      )}
      <button
        className="button danger"
        disabled={action.busy || usage.loading || !usage.data || !!usage.error}
        onClick={confirm}
      >
        {inUse ? 'Удалить у всех товаров' : 'Удалить'}
      </button>
      <button className="text-button" disabled={action.busy} onClick={onCancel}>
        Отмена
      </button>
    </section>
  );
}
