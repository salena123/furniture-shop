import { Breadcrumbs } from './Breadcrumbs';
import { PageHeading } from './PageHeading';
export function UnavailablePage({ title, description }) {
  return (
    <section className="content-page">
      <Breadcrumbs
        items={[
          {
            label: 'Каталог',
            href: '#/catalog',
          },
          {
            label: title,
          },
        ]}
      />
      <PageHeading title={title}>{description}</PageHeading>
      <a className="button primary" href="#/catalog">
        Перейти в каталог
      </a>
    </section>
  );
}
