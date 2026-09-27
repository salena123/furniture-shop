import { useState, useEffect } from 'react';
import { allPages } from '../services/api';
export function useReferences(revision, enabled) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: '',
  });
  useEffect(() => {
    if (!enabled) {
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
    Promise.all([
      allPages('/api/categories/?include_inactive=true', options),
      allPages('/api/materials/', options),
    ])
      .then(([categories, materials]) => {
        if (!controller.signal.aborted)
          setState({
            data: {
              categories,
              materials,
            },
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
  }, [revision, enabled]);
  return state;
}
