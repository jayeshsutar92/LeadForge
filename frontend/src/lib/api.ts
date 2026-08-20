import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env["VITE_API_URL"] || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => {
    // Standard token key for LeadForge authentication
    const token = typeof window !== "undefined" ? localStorage.getItem("leadforge_token") : null;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Automatically clear token on 401 Unauthorized
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("leadforge_token");
      // Redirection to login should be handled by an Auth provider or router event
    }
    return Promise.reject(error);
  },
);
