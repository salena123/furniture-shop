import { query } from '../../services/api';
import { ImagePlaceholder } from '../common/ImagePlaceholder';
export function ProductCard({ product, from }) {
  return (
    <a
      className="product-card"
      href={query(`#/product/${product.id}`, {
        from,
      })}
    >
      <ImagePlaceholder />
      <div className="product-description">
        <div className="card-meta">
          {product.is_custom ? 'По вашим размерам' : 'Готовое решение'}
        </div>
        <h2>{product.product_name}</h2>
        <p>
          {product.short_description ||
            product.material_name ||
            product.material ||
            'Подробнее о проекте'}
        </p>
        <div className="card-bottom">
          <strong>{product.price}</strong>
          <span>Подробнее →</span>
        </div>
      </div>
    </a>
  );
}
