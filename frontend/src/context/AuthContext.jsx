import { createContext, useState, useEffect, useContext, useCallback } from "react";
import authService from "../services/authService";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => {
    const val = localStorage.getItem("token") || sessionStorage.getItem("token");
    return (val === "null" || val === "undefined") ? null : val;
  });
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("refreshToken");
    setToken(null);
    setUser(null);
    setLoading(false);
  }, []);

  const checkUserAuth = useCallback(async () => {
    let activeToken = localStorage.getItem("token") || sessionStorage.getItem("token");
    if (activeToken === "null" || activeToken === "undefined") {
      activeToken = null;
    }
    
    if (!activeToken) {
      setUser(null);
      setLoading(false);
      return;
    }
    
    try {
      const response = await authService.getMe();
      setUser(response.data);
    } catch (error) {
      console.error("Auth verification check failed:", error);
      logout();
    } finally {
      setLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    checkUserAuth();
  }, [token, checkUserAuth]);

  const login = async (email, password, remember = true) => {
    setLoading(true);
    try {
      const response = await authService.login(email, password);
      const { access_token, refresh_token } = response.data;
      if (remember) {
        localStorage.setItem("token", access_token);
        localStorage.setItem("refreshToken", refresh_token);
      } else {
        sessionStorage.setItem("token", access_token);
        sessionStorage.setItem("refreshToken", refresh_token);
      }
      setToken(access_token);
      return true;
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const oauthLogin = async (provider, oauthData) => {
    setLoading(true);
    try {
      const response = await authService.oauthLogin(provider, oauthData);
      const { access_token, refresh_token } = response.data;
      
      // OAuth remembers by default
      localStorage.setItem("token", access_token);
      localStorage.setItem("refreshToken", refresh_token);
      
      setToken(access_token);
      return true;
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      await authService.register(name, email, password);
      // Auto login after registration (remembers by default)
      return await login(email, password, true);
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const completeOAuthLogin = (access_token, refresh_token) => {
    setLoading(true);
    localStorage.setItem("token", access_token);
    localStorage.setItem("refreshToken", refresh_token);
    setToken(access_token);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, oauthLogin, register, logout, completeOAuthLogin }}>
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
export default AuthContext;
