import { Breadcrumbs } from '../../components/common/Breadcrumbs';
import { AboutContent } from '../../components/common/AboutContent';
import { LoadState } from '../../components/common/Feedback';
import { useResource } from '../../hooks/useResource';

export function AboutPage({ onEnquiry }) {
  const resource = useResource('/api/site/about');
  return (
    <section className="content-page">
      <Breadcrumbs items={[{ label: 'О нас' }]} />
      <LoadState resource={resource} />
      {resource.data && <AboutContent page={resource.data} />}
      <div className="soft-panel project-cta">
        <div>
          <h2>С чего начнём?</h2>
          <p className="muted">Расскажите, какая мебель вам нужна.</p>
        </div>
        <div className="about-toolbar">
          <a className="button secondary" href="#/catalog">
            Посмотреть работы
          </a>
          <button className="button primary" onClick={() => onEnquiry()}>
            Обсудить проект
          </button>
        </div>
      </div>
    </section>
  );
}
