import { useState } from 'react';
import { sortedProductImages } from '../../utils/productImages';
import { ProductImage } from '../common/ProductImage';

export function ProductGallery({ product }) {
  const images = sortedProductImages(product.images);
  const [selectedId, setSelectedId] = useState(null);
  const selected = images.find((image) => image.id === selectedId) || images[0];

  return (
    <div>
      <ProductImage
        image={selected}
        alt={product.product_name}
        className="detail-photo"
        loading="eager"
      />
      {images.length > 1 && (
        <div className="photo-thumbnails" aria-label="Фотографии проекта">
          {images.map((image, index) => (
            <button
              key={image.id}
              className={`thumbnail ${selected?.id === image.id ? 'selected' : ''}`}
              aria-label={`Фотография ${index + 1}`}
              aria-pressed={selected?.id === image.id}
              onClick={() => setSelectedId(image.id)}
            >
              <ProductImage
                image={image}
                alt={`${product.product_name}: фотография ${index + 1}`}
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
