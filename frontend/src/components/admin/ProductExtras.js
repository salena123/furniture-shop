import { ProductAttributes } from './ProductAttributes';
import { ProductImages } from './ProductImages';
import { useResource } from '../../hooks/useResource';
import { useAction } from '../../hooks/useAction';
import { api } from '../../services/api';
import { Modal } from '../common/Modal';
import { LoadState, ErrorNotice } from '../common/Feedback';
export function ProductExtras({ item, onClose, onChanged }) {
  const resource = useResource(`/api/products/${item.id}?include_inactive=true`, {
    auth: true,
  });
  const options = useResource('/api/catalog/options');
  const action = useAction();
  const changed = () => {
    resource.reload();
    onChanged();
  };
  const mutate = (path, method, body, done) =>
    action.run(
      () =>
        api(path, {
          method,
          body,
          auth: true,
        }),
      () => {
        changed();
        done?.();
      },
    );
  return (
    <Modal title={item.product_name} onClose={onClose} busy={action.busy} wide>
      <LoadState resource={resource} />
      <ErrorNotice message={action.error} />
      {resource.data && (
        <>
          <ProductAttributes
            resource={resource}
            action={action}
            mutate={mutate}
            item={item}
            options={options}
          />
          <ProductImages resource={resource} mutate={mutate} action={action} item={item} />
        </>
      )}
    </Modal>
  );
}
