import { Modal } from './Modal';
import { RecordForm } from './RecordForm';

export default function RecordEditor({ title, ...props }) {
  return (
    <Modal title={title} onClose={props.onClose} busy={props.action.busy} wide>
      <RecordForm {...props} />
    </Modal>
  );
}
