import axios from "axios";

export function getAccessToken() {
  return localStorage.getItem("access_token");
}

export function setAccessToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function removeAccessToken() {
  localStorage.removeItem("access_token");
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export const getCurrentUser = () => {
  return api.get("/users/me");
};

export const getProfile = () => {
  return api.get("/profile");
};

export const createProfile = (profileData: unknown) => {
  return api.post("/profile", profileData);
};

export const updateProfile = (profileData: unknown) => {
  return api.put("/profile", profileData);
};

export const deleteProfile = () => {
  return api.delete("/profile");
};

export default api;
