import { createContext, useContext, useState, useCallback, useEffect } from "react";
import type { ReactNode } from "react";
import apiClient from "../api/client";

interface User {
  id: string;
  email: string;
}

interface UserContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<string>;
  logout: () => void;
  confirmEmail: (token: string) => Promise<string>;
  forgotPassword: (email: string) => Promise<string>;
  resetPassword: (token: string, password: string) => Promise<string>;
}

const UserContext = createContext<UserContextValue | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const [isLoading, setIsLoading] = useState(true);

  // Check existing token on mount
  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    apiClient
      .get("/auth/me")
      .then((res) => setUser(res.data as User))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
      })
      .finally(() => setIsLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiClient.post("/auth/login", { email, password });
    const { token: jwt, user: u } = res.data as { token: string; user: User };
    localStorage.setItem("token", jwt);
    setToken(jwt);
    setUser(u);
  }, []);

  const register = useCallback(async (email: string, password: string): Promise<string> => {
    const res = await apiClient.post("/auth/register", { email, password });
    return (res.data as { message: string }).message;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }, []);

  const confirmEmail = useCallback(async (tkn: string): Promise<string> => {
    const res = await apiClient.post("/auth/confirm-email", { token: tkn });
    return (res.data as { message: string }).message;
  }, []);

  const forgotPassword = useCallback(async (email: string): Promise<string> => {
    const res = await apiClient.post("/auth/forgot-password", { email });
    return (res.data as { message: string }).message;
  }, []);

  const resetPassword = useCallback(async (tkn: string, password: string): Promise<string> => {
    const res = await apiClient.post("/auth/reset-password", { token: tkn, password });
    return (res.data as { message: string }).message;
  }, []);

  return (
    <UserContext.Provider
      value={{ user, token, isLoading, login, register, logout, confirmEmail, forgotPassword, resetPassword }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within <UserProvider>");
  return ctx;
}
