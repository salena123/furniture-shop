import { useState, useCallback, useEffect } from 'react';
import { api } from '../services/api';
export function useResource(path, { auth = false, version = 0 } = {}) {
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({
    data: null,
    error: '',
    loading: !!path,
    path,
    auth,
  });
  const reload = useCallback(() => setRevision((value) => value + 1), []);
  useEffect(() => {
    if (!path) {
      setState({
        data: null,
        error: '',
        loading: false,
        path,
        auth,
      });
      return;
    }
    const controller = new AbortController();
    setState((previous) => ({
      data: previous.path === path && previous.auth === auth ? previous.data : null,
      error: '',
      loading: true,
      path,
      auth,
    }));
    api(path, {
      auth,
      signal: controller.signal,
    })
      .then((data) => {
        if (!controller.signal.aborted)
          setState({
            data,
            error: '',
            loading: false,
            path,
            auth,
          });
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setState((previous) => ({
            data:
              error.status === 404 || error.status === 401 || error.status === 403
                ? null
                : previous.data,
            error: error.message,
            status: error.status,
            loading: false,
            path,
            auth,
          }));
      });
    return () => controller.abort();
  }, [path, auth, version, revision]);
  return {
    ...(state.path === path && state.auth === auth
      ? state
      : {
          data: null,
          error: '',
          loading: !!path,
        }),
    reload,
  };
}
