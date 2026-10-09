import { useAction } from '../../hooks/useAction';
import { useState } from 'react';
import { api } from '../../services/api';
import { Modal } from '../common/Modal';
import { Field } from '../common/Field';
import { ErrorNotice } from '../common/Feedback';
export function EnquiryDialog({ product, onClose, options }) {
  const action = useAction();
  const [success, setSuccess] = useState(null);
  const submit = (event) => {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget));
    const body = {
      ...values,
      product_id: product?.id || null,
      product_name: product?.product_name || values.product_name,
      material_id: values.material_id ? Number(values.material_id) : null,
      needs_measurements: values.needs_measurements === 'on',
      personal_data_consent: values.personal_data_consent === 'on',
    };
    action.run(
      () =>
        api('/api/requests/', {
          method: 'POST',
          body,
        }),
      setSuccess,
    );
  };
  return (
    <Modal
      title={success ? 'Заявка отправлена' : 'Давайте обсудим вашу мебель'}
      onClose={onClose}
      busy={action.busy}
      wide
    >
      {success ? (
        <div className="success-state" role="status">
          <span className="success-mark">✓</span>
          <p>
            Спасибо, {success.client_name}! Ваша заявка №{success.id} принята.
          </p>
          <p className="muted">Сотрудник свяжется с вами по указанному телефону.</p>
          <button className="button primary" onClick={onClose}>
            Готово
          </button>
        </div>
      ) : (
        <form onSubmit={submit}>
          <p className="muted">
            {product
              ? `Проект: ${product.product_name}`
              : 'Заполните контакты и коротко опишите задачу.'}
          </p>
          <fieldset disabled={action.busy}>
            <label className="bot-trap" aria-hidden="true">
              Не заполняйте это поле
              <input name="website" tabIndex="-1" autoComplete="off" />
            </label>
            <div className="form-grid">
              <Field
                label="Ваше имя"
                name="client_name"
                autoComplete="name"
                required
                maxLength={100}
              />
              <Field
                label="Телефон"
                name="phone"
                type="tel"
                autoComplete="tel"
                required
                minLength={7}
                maxLength={25}
                placeholder="+7 (___) ___-__-__"
              />
              {!product && (
                <Field
                  className="full-width"
                  label="Какая мебель нужна?"
                  name="product_name"
                  required
                  placeholder="Например, угловая кухня"
                />
              )}
              <Field label="Город" name="city" autoComplete="address-level2" />
              <Field
                label="Когда удобно связаться?"
                name="preferred_contact_time"
                placeholder="Например, после 18:00"
              />
              <Field
                label="Материал"
                name="material_id"
                type="select"
                defaultValue={product?.material_id || ''}
                options={[
                  {
                    value: '',
                    label: 'Помогите выбрать',
                  },
                  ...(options.data?.materials || []).map((item) => ({
                    value: item.id,
                    label: item.name,
                  })),
                ]}
              />
              <Field label="Цвет" name="color_name" defaultValue={product?.color || ''} />
              <Field label="Примерные размеры" name="dimensions" placeholder="Если уже известны" />
              <Field label="Нужен замер" name="needs_measurements" type="checkbox" defaultChecked />
              <Field
                className="full-width"
                label="Ваши пожелания"
                name="comment"
                type="textarea"
                maxLength={4000}
              />
            </div>
            <Field
              label="Согласен на обработку имени, телефона и сведений из заявки для связи и обсуждения заказа."
              name="personal_data_consent"
              type="checkbox"
              required
            />
            <ErrorNotice message={action.error} />
            <button className="button primary" type="submit">
              {action.busy ? 'Отправка…' : 'Отправить заявку'}
            </button>
          </fieldset>
        </form>
      )}
    </Modal>
  );
}
