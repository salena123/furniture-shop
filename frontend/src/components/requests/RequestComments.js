import { useState } from 'react';
import { dateTime } from '../../utils/dateTime';
import { Field } from '../common/Field';
export function RequestComments({ request, user, openModal, mutate, id, busy }) {
  const [comment, setComment] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    mutate(`/api/requests/${id}/comments`, 'POST', { comment_text: comment.trim() }, () =>
      setComment(''),
    );
  };

  return (
    <section className="surface padded">
      <h2>
        Комментарии сотрудников <span className="count">{request.comments.length}</span>
      </h2>
      <div className="comments-list">
        {request.comments.map((item) => (
          <article className="comment" key={item.id}>
            <div className="comment-meta">
              <strong>{item.user_name || 'Сотрудник'}</strong>
              <time>{dateTime(item.created_at)}</time>
            </div>
            <p className="multiline">{item.comment_text}</p>
            {(user.role === 'admin' || item.user_id === user.id) && (
              <div className="inline-actions">
                <button
                  className="text-button"
                  onClick={() =>
                    openModal({
                      type: 'comment',
                      item,
                    })
                  }
                >
                  Изменить
                </button>
                <button
                  className="text-button danger-text"
                  onClick={() =>
                    openModal({
                      type: 'delete-comment',
                      item,
                    })
                  }
                >
                  Удалить
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <Field
          label="Новый комментарий"
          type="textarea"
          required
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Итоги разговора, договорённости, следующий шаг"
        />
        <button className="button primary" disabled={busy || !comment.trim()}>
          Добавить комментарий
        </button>
      </form>
    </section>
  );
}
