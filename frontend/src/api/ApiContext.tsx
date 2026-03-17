import { createContext, useContext, useMemo, useState, useCallback } from "react";
import type { ReactNode } from "react";
import type { AxiosRequestConfig, AxiosResponse } from "axios";
import apiClient from "./client";

// ── Types ──────────────────────────────────────────────────────────────

interface ApiContextValue {
  token: string | null;
  setToken: (token: string | null) => void;
  get: <T = unknown>(url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
  patch: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
  del: <T = unknown>(url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
}

// ── Context ────────────────────────────────────────────────────────────

const ApiContext = createContext<ApiContextValue | null>(null);

// ── Provider ───────────────────────────────────────────────────────────

export function ApiProvider({ children }: { children: ReactNode }) {
  const [token, _setToken] = useState<string | null>(
    () => localStorage.getItem("token")
  );

  const setToken = useCallback((newToken: string | null) => {
    _setToken(newToken);
    if (newToken) {
      localStorage.setItem("token", newToken);
    } else {
      localStorage.removeItem("token");
    }
  }, []);

  // ── HTTP helpers ───────────────────────────────────────────────────

  const get = useCallback(
    <T = unknown,>(url: string, config?: AxiosRequestConfig) =>
      apiClient.get<T>(url, config),
    []
  );

  const post = useCallback(
    <T = unknown,>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
      apiClient.post<T>(url, data, config),
    []
  );

  const put = useCallback(
    <T = unknown,>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
      apiClient.put<T>(url, data, config),
    []
  );

  const patch = useCallback(
    <T = unknown,>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
      apiClient.patch<T>(url, data, config),
    []
  );

  const del = useCallback(
    <T = unknown,>(url: string, config?: AxiosRequestConfig) =>
      apiClient.delete<T>(url, config),
    []
  );

  // ── Value ──────────────────────────────────────────────────────────

  const value = useMemo<ApiContextValue>(
    () => ({ token, setToken, get, post, put, patch, del }),
    [token, setToken, get, post, put, patch, del]
  );

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

// ── Hook ───────────────────────────────────────────────────────────────

export function useApi(): ApiContextValue {
  const ctx = useContext(ApiContext);
  if (!ctx) {
    throw new Error("useApi must be used within an <ApiProvider>");
  }
  return ctx;
}
