import { useState } from 'react';
import { productImageUrl } from '../../utils/productImages';
import { ImagePlaceholder } from './ImagePlaceholder';

function ImageContent({ src, alt, loading }) {
  const [failed, setFailed] = useState(false);

  if (!src || failed) {
    return (
      <ImagePlaceholder label={failed ? 'Не удалось загрузить фотографию' : 'Фотография проекта'} />
    );
  }

  return <img src={src} alt={alt} loading={loading} onError={() => setFailed(true)} />;
}

export function ProductImage({
  image,
  alt = 'Фотография проекта',
  className = '',
  loading = 'lazy',
}) {
  const src = productImageUrl(image?.image_url);

  return (
    <div className={`product-image ${className}`}>
      <ImageContent key={src} src={src} alt={image?.alt_text || alt} loading={loading} />
    </div>
  );
}
