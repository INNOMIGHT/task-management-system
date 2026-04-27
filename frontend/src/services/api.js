import axios from "axios";

const API = axios.create({
  baseURL: "https://task-management-system-production-9505.up.railway.app/",
});

// attach token automatically
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("token");
  if (token) {
    req.headers.Authorization = `Bearer ${token}`;
  }
  return req;
});

export default API;