export function ClientProject({ openModal, request }) {
  return (
    <section className="surface padded">
      <div className="section-top">
        <h2>Клиент и проект</h2>
        <button
          className="text-button"
          onClick={() =>
            openModal({
              type: 'edit',
            })
          }
        >
          Редактировать
        </button>
      </div>
      <dl className="details-list">
        {[
          ['Имя', request.client_name],
          ['Телефон', <a href={`tel:${request.phone.replace(/[^+\d]/g, '')}`}>{request.phone}</a>],
          ['Город', request.city],
          ['Удобное время', request.preferred_contact_time],
          [
            'Проект',
            request.product_id ? (
              <a href={`#/product/${request.product_id}`}>{request.product_name} ↗</a>
            ) : (
              request.product_name
            ),
          ],
          ['Материал', request.material_name],
          ['Цвет', request.color_name],
          ['Размеры', request.dimensions],
          ['Замер', request.needs_measurements ? 'Нужен' : 'Не требуется'],
        ].map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value || 'Не указано'}</dd>
          </div>
        ))}
      </dl>
      {request.comment && (
        <div className="client-note">
          <h3>Пожелания клиента</h3>
          <p className="multiline">{request.comment}</p>
        </div>
      )}
    </section>
  );
}
