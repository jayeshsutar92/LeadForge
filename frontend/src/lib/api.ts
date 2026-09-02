import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env["VITE_API_URL"] || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
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

export interface ApiError {
  response?: {
    status?: number;
    statusText?: string;
    data?: any;
  };
  message?: string;
}

export function getErrorMessage(err: unknown): string {
  const error = err as ApiError;

  if (error.response) {
    if (error.response.data) {
      const data = error.response.data;
      if (typeof data.detail === "string") {
        return data.detail;
      }
      if (data.detail && !Array.isArray(data.detail) && data.detail.message) {
        return data.detail.message;
      }
      if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0]?.msg) {
        return data.detail[0].msg;
      }
      if (data.error?.message) {
        return data.error.message;
      }
      if (typeof data === "string" && data.length > 0 && data.length < 200) {
        return data;
      }
    }
    
    if (error.response.status === 500) {
      return "Internal Server Error: The backend encountered an unexpected problem.";
    }
    if (error.response.status === 404) {
      return "Not Found: The requested resource could not be found on the server.";
    }
    if (error.response.status === 403) {
      return "Forbidden: You do not have permission to perform this action.";
    }
    if (error.response.statusText) {
      return `Server Error: ${error.response.statusText}`;
    }
  }

  if (error.message === "Network Error") {
    return "Network Error: Unable to reach the server. Please check your connection.";
  }

  return error.message || "An unexpected error occurred.";
}
