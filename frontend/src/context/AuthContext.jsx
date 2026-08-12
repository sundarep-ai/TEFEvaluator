import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { login as apiLogin, register as apiRegister, getMe } from '../api/index.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Distinguishes "not logged in" from "we haven't checked yet". Without this,
  // the router renders the redirect-to-login branch before the token check
  // finishes and bounces an authenticated user on every page load.
  const [initialising, setInitialising] = useState(true);

  // Restore the session from the stored JWT on mount. Previously `user` lived
  // only in React state, so any refresh (or opening a deep link) logged the
  // user out even though a valid token was sitting in localStorage.
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setInitialising(false);
      return;
    }
    let cancelled = false;
    getMe()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        // Expired or invalid token — clear it rather than retrying forever.
        localStorage.removeItem('token');
      })
      .finally(() => {
        if (!cancelled) setInitialising(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (username, password) => {
    const data = await apiLogin(username, password);
    localStorage.setItem('token', data.access_token);
    const me = await getMe();
    setUser(me);
    return me;
  }, []);

  const register = useCallback(async (username, password) => {
    await apiRegister(username, password);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('token');
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, login, register, logout, isAuthenticated: !!user, initialising }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
