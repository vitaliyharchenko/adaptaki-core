import { createContext, useContext, useEffect, useState } from "react";
import api from "./api";

export type User = {
  id: number;
  username: string;
  role: string;
};

type AuthContextType = {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  const fetchMe = async () => {
    try {
      const res = await api.get("/auth/me/");
      setUser(res.data);
    } catch {
      setUser(null);
    }
  };

  useEffect(() => {
    if (localStorage.getItem("access_token")) {
      fetchMe();
    }
  }, []);

  const login = async (username: string, password: string) => {
    const res = await api.post("/auth/login/", { username, password });
    localStorage.setItem("access_token", res.data.access);
    await fetchMe();
  };

  const register = async (username: string, password: string) => {
    await api.post("/auth/register/", { username, password });
    await login(username, password);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};
