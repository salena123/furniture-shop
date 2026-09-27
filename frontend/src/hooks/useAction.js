import { useRef, useState } from 'react';
export function useAction() {
  const running = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const run = async (task, onSuccess) => {
    if (running.current) return;
    running.current = true;
    setBusy(true);
    setError('');
    try {
      const result = await task();
      await onSuccess?.(result);
    } catch (error) {
      setError(error.message);
    } finally {
      running.current = false;
      setBusy(false);
    }
  };
  return {
    busy,
    error,
    run,
    clearError: () => setError(''),
  };
}
