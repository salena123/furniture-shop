import { createContext, useState, useCallback, useEffect, useContext } from 'react';
import { session, api } from '../services/api';
export const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [token, setToken] = useState(session.get);
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(!!token);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const logout = useCallback(() => {
    session.set(null);
    setToken(null);
    setUser(null);
    setError('');
  }, []);
  useEffect(() => {
    const expired = () => {
      logout();
      setError('Сессия завершилась. Войдите снова.');
    };
    window.addEventListener('maestro:session-expired', expired);
    return () => window.removeEventListener('maestro:session-expired', expired);
  }, [logout]);
  useEffect(() => {
    if (!token) {
      setChecking(false);
      return;
    }
    const controller = new AbortController();
    setChecking(true);
    setError('');
    api('/api/auth/me', {
      auth: true,
      signal: controller.signal,
    })
      .then((data) => {
        if (!controller.signal.aborted) setUser(data);
      })
      .catch((error) => {
        if (!controller.signal.aborted) setError(error.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setChecking(false);
      });
    return () => controller.abort();
  }, [token, revision]);
  const login = async (credentials) => {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: credentials,
    });
    session.set(data.access_token);
    setUser(data.user);
    setToken(data.access_token);
    setError('');
  };
  return (
    <AuthContext.Provider
      value={{
        user,
        checking,
        error,
        login,
        logout,
        refresh: () => setRevision((v) => v + 1),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
export const useAuth = () => useContext(AuthContext);
