import { useResource } from '../../hooks/useResource';
import { UnavailablePage } from '../../components/common/UnavailablePage';
import { catalogReturnLocation, categoryAncestors } from '../../utils/navigation';
import { Breadcrumbs } from '../../components/common/Breadcrumbs';
import { LoadState } from '../../components/common/Feedback';
import { ProductGallery } from '../../components/catalog/ProductGallery';
import { PageHeading } from '../../components/common/PageHeading';
import { productDetails } from '../../utils/productDetails';
export function ProductPage({ id, searchParams = '', options, onEnquiry }) {
  const resource = useResource(`/api/products/${id}`);
  const product = resource.data;
  const category = options.data?.categories.find((item) => item.id === product?.category_id);
  const details = productDetails(product);
  if (resource.status === 404)
    return (
      <UnavailablePage
        title="Проект недоступен"
        description="Возможно, его сняли с публикации или переместили. Вы можете выбрать другой проект в каталоге."
      />
    );
  return (
    <section className="content-page">
      <a className="back-link" href={catalogReturnLocation(searchParams)}>
        ← Вернуться к работам
      </a>
      <Breadcrumbs
        items={[
          {
            label: 'Каталог',
            href: '#/catalog',
          },
          ...categoryAncestors(category, options.data?.categories),
          ...(category
            ? [
                {
                  label: category.name,
                  href: `#/catalog/${category.id}`,
                },
              ]
            : []),
          {
            label: product?.product_name || 'Проект',
          },
        ]}
      />
      <LoadState resource={resource} />
      {product && (
        <>
          <div className="product-detail">
            <ProductGallery key={product.id} product={product} />
            <div className="product-summary">
              <PageHeading
                eyebrow={product.is_custom ? 'Мебель на заказ' : 'Наши работы'}
                title={product.product_name}
              >
                {product.short_description}
              </PageHeading>
              <p className="product-price">{product.price}</p>
              <dl className="details-list">
                {details.map(([label, value], index) => (
                  <div key={index}>
                    <dt>{label}</dt>
                    <dd>{value}</dd>
                  </div>
                ))}
              </dl>
              <button className="button primary" onClick={() => onEnquiry(product)}>
                Обсудить проект
              </button>
              <p className="muted">Расскажите о пожеланиях — обсудим детали в ответ на заявку.</p>
            </div>
          </div>
          {product.description && (
            <div className="description-panel">
              <h2>О проекте</h2>
              <p className="multiline">{product.description}</p>
            </div>
          )}
          <div className="soft-panel project-cta">
            <div>
              <h2>Нужен другой размер или цвет?</h2>
              <p className="muted">Оставьте пожелания в заявке.</p>
            </div>
            <button className="button secondary" onClick={() => onEnquiry(product)}>
              Оставить заявку
            </button>
          </div>
        </>
      )}
    </section>
  );
}
