import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("usuario");

      if (window.location.pathname !== "/") {
        window.location.assign("/");
      }
    }

    return Promise.reject(error);
  }
);

export const mensajeError = (error, respaldo) => {
  const detalle = error?.response?.data?.detail;

  if (typeof detalle === "string" && detalle.trim()) {
    return detalle;
  }

  if (Array.isArray(detalle)) {
    const textos = detalle
      .map((item) => item?.msg || item?.detail || "")
      .filter(Boolean);

    if (textos.length > 0) {
      return textos.join(" ");
    }
  }

  if (!error?.response) {
    return "No se pudo conectar con el backend. Verifique que esté encendido en http://127.0.0.1:8000.";
  }

  return respaldo;
};

export default api;
