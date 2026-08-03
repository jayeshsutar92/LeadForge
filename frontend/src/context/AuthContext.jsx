import { createContext, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null); // null = loading, false = anon, obj = user
    const [initialized, setInitialized] = useState(false);

    useEffect(() => {
        (async () => {
            try {
                const { data } = await api.get("/api/auth/me");
                setUser(data);
            } catch {
                setUser(false);
            } finally {
                setInitialized(true);
            }
        })();
    }, []);

    const login = async (email, password) => {
        const { data } = await api.post("/api/auth/login", { email, password });
        if (data.access_token) localStorage.setItem("access_token", data.access_token);
        setUser(data);
        return data;
    };

    const register = async (name, email, password) => {
        const { data } = await api.post("/api/auth/register", { name, email, password });
        if (data.access_token) localStorage.setItem("access_token", data.access_token);
        setUser(data);
        return data;
    };

    const logout = async () => {
        try { await api.post("/api/auth/logout"); } catch { }
        localStorage.removeItem("access_token");
        setUser(false);
    };

    return (
        <AuthContext.Provider value={{ user, initialized, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
