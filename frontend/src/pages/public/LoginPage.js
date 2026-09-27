import { useAuth } from '../../context/AuthContext';
import { useAction } from '../../hooks/useAction';
import { Field } from '../../components/common/Field';
import { ErrorNotice } from '../../components/common/Feedback';
export function LoginPage() {
  const auth = useAuth();
  const action = useAction();
  return (
    <section className="login-page">
      <div className="login-intro">
        <p className="eyebrow">Маэстро · рабочее пространство</p>
        <h1>
          Всё для работы
          <br />в одном месте
        </h1>
        <p>Заявки клиентов, проекты и управление каталогом.</p>
        <a className="back-link" href="#/">
          ← Вернуться на сайт
        </a>
      </div>
      <div className="surface login-form">
        <h2>Вход для сотрудников</h2>
        <p className="muted">Используйте логин и пароль, выданные администратором.</p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            const body = Object.fromEntries(new FormData(event.currentTarget));
            action.run(
              () => auth.login(body),
              () => {
                window.location.hash = '#/staff';
              },
            );
          }}
        >
          <fieldset disabled={action.busy || auth.checking}>
            <Field
              label="Логин"
              name="login"
              required
              autoComplete="username"
              autoCapitalize="none"
            />
            <Field
              label="Пароль"
              name="password"
              type="password"
              required
              autoComplete="current-password"
            />
            <ErrorNotice message={action.error || auth.error} />
            <button className="button primary" type="submit">
              {action.busy || auth.checking ? 'Входим…' : 'Войти'}
            </button>
          </fieldset>
        </form>
      </div>
    </section>
  );
}
