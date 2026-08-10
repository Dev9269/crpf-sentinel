"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { clearToken, getStoredUser, getToken, getTokenStorage, setStoredUser, setToken } from "@/lib/api";
import { authService } from "@/services";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string, rememberMe: boolean) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  can: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(() => getStoredUser<User>());
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    try {
      const me = await authService.me();
      setUser(me);
      const storage = getTokenStorage();
      setStoredUser(me, storage === window.sessionStorage ? false : true);
    } catch {
      clearToken();
      setUser(null);
      setTokenState(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(
    async (username: string, password: string, rememberMe: boolean) => {
      const result = await authService.login(username, password, rememberMe);
      setToken(result.access_token, rememberMe);
      setStoredUser(result.user, rememberMe);
      setTokenState(result.access_token);
      setUser(result.user);
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      /* token may already be invalid */
    }
    clearToken();
    setUser(null);
    setTokenState(null);
    router.push("/login");
  }, [router]);

  const hasPermission = useCallback(
    (permission: string) => {
      if (!user?.role) return false;
      if (user.role.name === "super_admin") return true;
      return user.role.permissions.includes(permission);
    },
    [user],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      login,
      logout,
      refresh,
      hasPermission,
      can: hasPermission,
    }),
    [user, token, loading, login, logout, refresh, hasPermission],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
