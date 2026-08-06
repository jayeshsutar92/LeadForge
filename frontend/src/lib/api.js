import axios from "axios";

// Use VITE_BACKEND_URL if set, otherwise use relative path so Vite's proxy works in dev
const BASE = import.meta.env.VITE_BACKEND_URL || "";

export const api = axios.create({
    baseURL: BASE,
    withCredentials: true,
});

// attach bearer token from localStorage as fallback (in case cookies blocked)
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// handle 401 unauthorized errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("access_token");
            // If not already on login/register, redirect
            if (!window.location.pathname.match(/^\/(login|register)/)) {
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

export function formatApiError(detail) {
    if (detail == null) return "Something went wrong.";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
        return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
    if (detail && typeof detail.msg === "string") return detail.msg;
    return String(detail);
}
