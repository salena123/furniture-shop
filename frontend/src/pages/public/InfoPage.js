import { Breadcrumbs } from '../../components/common/Breadcrumbs';
import { PageHeading } from '../../components/common/PageHeading';
import { ImagePlaceholder } from '../../components/common/ImagePlaceholder';
import { contacts } from '../../config/contacts';
export function InfoPage({ type, onEnquiry }) {
  const about = type === 'about';
  return (
    <section className="content-page">
      <Breadcrumbs
        items={[
          {
            label: about ? 'О нас' : 'Контакты',
          },
        ]}
      />
      <PageHeading
        eyebrow="Мастерская мебели «Маэстро»"
        title={about ? 'Мебель для вашего дома' : 'Давайте обсудим ваш проект'}
      >
        {about
          ? 'Изготовление качественной и функциональной мебели.'
          : 'Оставьте заявку — сотрудник свяжется с вами.'}
      </PageHeading>
      {about ? (
        <>
          <div className="about-layout">
            <ImagePlaceholder label="Фотография мастерской" />
            <div className="soft-panel">
              <h2>Индивидуальное решение начинается с ваших пожеланий</h2>
              <p className="muted">
                Посмотрите проекты в каталоге и расскажите, какую мебель вы представляете в своём
                доме. В заявке можно указать размеры, материал, цвет и необходимость замера.
              </p>
              <a className="button primary" href="#/catalog">
                Посмотреть работы
              </a>
            </div>
          </div>
          <h2 className="section-heading">Как обсудить проект</h2>
          <div className="steps-grid">
            {[
              ['01', 'Выберите направление', 'Кухня, шкаф или другое решение из каталога.'],
              ['02', 'Расскажите о пожеланиях', 'Укажите размеры и детали, которые важны для вас.'],
              ['03', 'Обсудите с сотрудником', 'Оставьте удобное время для обратной связи.'],
            ].map(([number, title, text]) => (
              <div className="surface step" key={number}>
                <span>{number}</span>
                <h3>{title}</h3>
                <p className="muted">{text}</p>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="contacts-layout">
          <div className="contact-grid">
            {[
              [
                'Телефон',
                contacts.phone,
                contacts.phone ? `tel:${contacts.phone.replace(/[^+\d]/g, '')}` : null,
              ],
              ['Адрес', contacts.address],
              ['Часы работы', contacts.hours],
              ['Почта', contacts.email, contacts.email ? `mailto:${contacts.email}` : null],
            ].map(([label, value, href]) => (
              <div className="surface contact-item" key={label}>
                <p className="eyebrow">{label}</p>
                {href ? <a href={href}>{value}</a> : <p>{value || 'Информация скоро появится'}</p>}
              </div>
            ))}
          </div>
          <ImagePlaceholder label="Место для карты и адреса мастерской" />
        </div>
      )}
      <div className="soft-panel project-cta">
        <div>
          <h2>С чего начнём?</h2>
          <p className="muted">Расскажите, какая мебель вам нужна.</p>
        </div>
        <button className="button primary" onClick={() => onEnquiry()}>
          Оставить заявку
        </button>
      </div>
    </section>
  );
}
