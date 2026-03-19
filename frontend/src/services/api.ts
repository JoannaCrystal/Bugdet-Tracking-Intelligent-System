/**
 * Base API client
 */

import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || err.message || "Request failed";
    return Promise.reject(new Error(typeof message === "string" ? message : JSON.stringify(message)));
  }
);
