import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  const url = config.url ?? "";
  const isAuthEndpoint = url.startsWith("/auth/login/") || url.startsWith("/auth/register/");
  if (token && !isAuthEndpoint) {
    config.headers.Authorization = `Bearer ${token}`;
  } else if (isAuthEndpoint && config.headers?.Authorization) {
    delete config.headers.Authorization;
  }
  return config;
});

export default api;
