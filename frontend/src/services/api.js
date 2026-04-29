import axios from "axios";

const API = axios.create({
  baseURL: "https://task-management-system-production-9505.up.railway.app/",
});

// attach token automatically
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("token");

  // DO NOT attach token for auth routes
  if (token && !req.url.includes("/login") && !req.url.includes("/register")) {
    req.headers.Authorization = `Bearer ${token}`;
  }

  return req;
});

export default API;