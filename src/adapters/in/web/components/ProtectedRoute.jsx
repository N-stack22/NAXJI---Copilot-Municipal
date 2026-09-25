import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { logout, obtenerUsuarioActual } from "../services/authService";

function ProtectedRoute({ children }) {
  const [estado, setEstado] = useState("cargando");

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      setEstado("sin-sesion");
      return;
    }

    obtenerUsuarioActual()
      .then(() => setEstado("ok"))
      .catch(() => {
        logout();
        setEstado("sin-sesion");
      });
  }, []);

  if (estado === "cargando") {
    return <p style={{ padding: "30px" }}>Comprobando sesión con el backend...</p>;
  }

  if (estado === "sin-sesion") {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default ProtectedRoute;
