import { LoadState, EmptyState } from '../common/Feedback';
import { ProductCard } from '../catalog/ProductCard';
import { useResource } from '../../hooks/useResource';
export function FeaturedWorks({ onEnquiry }) {
  const works = useResource('/api/products/?limit=3&offset=0');
  return (
    <section className="home-works" aria-labelledby="home-works-title">
      <div className="home-section-heading">
        <div>
          <h2 id="home-works-title">Наши работы</h2>
          <p>Идеи для кухни и других комнат вашего дома.</p>
        </div>
        <a className="home-all-works" href="#/catalog">
          Смотреть все <span aria-hidden="true">→</span>
        </a>
      </div>
      <LoadState resource={works} />
      {works.data &&
        (works.data.items.length ? (
          <div className="product-grid home-work-grid">
            {works.data.items.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <EmptyState title="Скоро здесь появятся наши работы">
            <p className="muted">А пока расскажите, какую мебель вы хотели бы заказать.</p>
            <button className="button secondary" onClick={() => onEnquiry()}>
              Обсудить проект
            </button>
          </EmptyState>
        ))}
    </section>
  );
}
