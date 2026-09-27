import { useState, useEffect } from 'react';
import { api, allPages } from '../services/api';
export function useLists(section, revision) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: '',
  });
  useEffect(() => {
    if (section === 'products') {
      setState({
        data: null,
        loading: false,
        error: '',
      });
      return;
    }
    const controller = new AbortController();
    const options = {
      auth: true,
      signal: controller.signal,
    };
    setState({
      data: null,
      loading: true,
      error: '',
    });
    const task =
      section === 'users'
        ? api('/api/users/', options)
        : allPages(
            `/api/${section}/${['categories', 'attributes'].includes(section) ? '?include_inactive=true' : ''}`,
            options,
          );
    task
      .then((data) => {
        if (!controller.signal.aborted)
          setState({
            data,
            loading: false,
            error: '',
          });
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setState({
            data: null,
            loading: false,
            error: error.message,
          });
      });
    return () => controller.abort();
  }, [section, revision]);
  return state;
}
