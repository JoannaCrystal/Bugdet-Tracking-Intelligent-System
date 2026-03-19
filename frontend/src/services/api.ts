/**
 * Base API client
 */

import axios from "axios";

// Empty = relative URLs (same origin). Set for dev: http://localhost:8000
const API_BASE = import.meta.env.VITE_API_URL ?? "";

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
