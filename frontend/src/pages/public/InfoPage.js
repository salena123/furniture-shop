import { Breadcrumbs } from '../../components/common/Breadcrumbs';
import { PageHeading } from '../../components/common/PageHeading';
import { ImagePlaceholder } from '../../components/common/ImagePlaceholder';
import { resolveContacts } from '../../config/contacts';
import { useResource } from '../../hooks/useResource';
import { LoadState } from '../../components/common/Feedback';
import { AboutPage } from './AboutPage';
export function InfoPage({ type, onEnquiry }) {
  return type === 'about' ? (
    <AboutPage onEnquiry={onEnquiry} />
  ) : (
    <ContactsInfoPage onEnquiry={onEnquiry} />
  );
}

function ContactsInfoPage({ onEnquiry }) {
  const resource = useResource('/api/site/contacts');
  const contacts = resolveContacts(resource.data);
  return (
    <section className="content-page">
      <Breadcrumbs
        items={[
          {
            label: 'Контакты',
          },
        ]}
      />
      <PageHeading eyebrow="Мастерская мебели «Маэстро»" title="Давайте обсудим ваш проект">
        Оставьте заявку — сотрудник свяжется с вами.
      </PageHeading>
      <LoadState resource={resource} />
      {resource.data && (
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
                {href ? (
                  <a href={href}>{value}</a>
                ) : (
                  <p className="multiline">{value || 'Информация скоро появится'}</p>
                )}
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
