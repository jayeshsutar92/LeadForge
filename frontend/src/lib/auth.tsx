import React, { createContext, useContext, useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { apiClient } from "./api";

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: any) => Promise<void>;
  register: (credentials: any) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("leadforge_token");
      if (token) {
        const response = await apiClient.get("/auth/me");
        setUser(response.data);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      setUser(null);
      localStorage.removeItem("leadforge_token");
      queryClient.clear();
      router.invalidate();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: any) => {
    const response = await apiClient.post("/auth/login", credentials);
    const { access_token, ...userData } = response.data;
    localStorage.setItem("leadforge_token", access_token);
    setUser(userData);
    queryClient.clear();
    router.invalidate();
  };

  const register = async (credentials: any) => {
    const response = await apiClient.post("/auth/register", credentials);
    const { access_token, ...userData } = response.data;
    localStorage.setItem("leadforge_token", access_token);
    setUser(userData);
    queryClient.clear();
    router.invalidate();
  };

  const logout = async () => {
    try {
      await apiClient.post("/auth/logout");
    } catch (e) {
      console.error("Logout failed on server", e);
    }
    localStorage.removeItem("leadforge_token");
    setUser(null);
    queryClient.clear();
    router.invalidate();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
