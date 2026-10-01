import { fireEvent, render, screen } from '@testing-library/react';
import { API_BASE } from '../../services/api';
import { productImageUrl } from '../../utils/productImages';
import { ProductImage } from '../common/ProductImage';
import { ProductImages } from '../admin/ProductImages';
import { ProductCard } from './ProductCard';
import { ProductGallery } from './ProductGallery';

const images = [
  { id: 1, image_url: '/static/products/8/side.jpg', alt_text: 'Вид сбоку', sort_order: 2 },
  {
    id: 2,
    image_url: '/static/products/8/main.jpg',
    alt_text: 'Общий вид',
    sort_order: 5,
    is_main: true,
  },
  { id: 3, image_url: 'https://example.com/detail.jpg', alt_text: 'Детали кухни', sort_order: 1 },
];
const product = { id: 8, product_name: 'Угловая кухня', price: 'По запросу', images };

test('resolves uploaded files against the backend and preserves external image URLs', () => {
  expect(productImageUrl(images[0].image_url)).toBe(`${API_BASE}/static/products/8/side.jpg`);
  expect(productImageUrl('static/photo.png')).toBe(`${API_BASE}/static/photo.png`);
  expect(productImageUrl(images[2].image_url)).toBe(images[2].image_url);
  expect(productImageUrl(null)).toBe('');
  expect(productImageUrl('javascript:alert(1)')).toBe('');
});

test('catalog card displays the main image even when it is not first in API data', () => {
  render(<ProductCard product={product} />);
  expect(screen.getByRole('img', { name: 'Общий вид' })).toHaveAttribute(
    'src',
    `${API_BASE}${images[1].image_url}`,
  );
  expect(images.map((image) => image.id)).toEqual([1, 2, 3]);
});

test('gallery starts with the main image and switches to ordered photographs', () => {
  const { container } = render(<ProductGallery product={product} />);
  expect(container.querySelector('.detail-photo img')).toHaveAttribute('alt', 'Общий вид');
  fireEvent.click(screen.getByRole('button', { name: 'Фотография 2', exact: true }));
  expect(container.querySelector('.detail-photo img')).toHaveAttribute('src', images[2].image_url);
  expect(screen.getByRole('button', { name: 'Фотография 2', exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
});

test('missing and failed images use placeholders, and a different image can still load', () => {
  const { rerender } = render(<ProductImage />);
  expect(screen.getByRole('img', { name: 'Фотография проекта' }).tagName).toBe('DIV');
  rerender(<ProductImage image={images[0]} />);
  fireEvent.error(screen.getByRole('img', { name: 'Вид сбоку' }));
  expect(screen.getByRole('img', { name: 'Не удалось загрузить фотографию' })).toBeInTheDocument();
  rerender(<ProductImage image={images[1]} />);
  expect(screen.getByRole('img', { name: 'Общий вид' }).tagName).toBe('IMG');
});

test('administrator sees previews including a newly loaded photo', () => {
  const props = { item: product, action: { busy: false }, mutate: jest.fn() };
  const { rerender } = render(
    <ProductImages {...props} resource={{ data: { images: [images[0]] } }} />,
  );
  expect(screen.getByRole('img', { name: 'Вид сбоку' })).toBeInTheDocument();
  rerender(<ProductImages {...props} resource={{ data: { images } }} />);
  expect(screen.getAllByRole('img')).toHaveLength(3);
  expect(screen.getByRole('img', { name: 'Общий вид' })).toHaveAttribute(
    'src',
    `${API_BASE}${images[1].image_url}`,
  );
});
