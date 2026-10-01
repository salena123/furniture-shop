import { createContext, useState, useCallback, useEffect, useContext } from 'react';
import { api } from '../services/api';
export const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const clearSession = useCallback(() => {
    setUser(null);
    setError('');
  }, []);
  const logout = useCallback(async () => {
    try {
      await api('/api/auth/logout', { method: 'POST', auth: true });
      clearSession();
      return true;
    } catch (error) {
      if (error.status === 401) {
        clearSession();
        return true;
      }
      setError('Не удалось завершить сессию на сервере. Попробуйте выйти ещё раз.');
      return false;
    }
  }, [clearSession]);
  useEffect(() => {
    const expired = () => {
      clearSession();
      setError('Сессия завершилась. Войдите снова.');
    };
    window.addEventListener('maestro:session-expired', expired);
    return () => window.removeEventListener('maestro:session-expired', expired);
  }, [clearSession]);
  useEffect(() => {
    // Remove legacy tokens; authentication now uses HttpOnly cookies.
    sessionStorage.removeItem('maestro.staff.token');
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
        if (!controller.signal.aborted) {
          if (error.status === 401) setUser(null);
          else setError(error.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setChecking(false);
      });
    return () => controller.abort();
  }, [revision]);
  const login = async (credentials) => {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: credentials,
    });
    setUser(data.user);
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
