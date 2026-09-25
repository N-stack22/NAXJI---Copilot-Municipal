import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { login, USUARIOS_DEMO } from "../services/authService";
import { mensajeError } from "../services/api";

function Login() {
  const navigate = useNavigate();

  const [usuario, setUsuario] = useState("demo-funcionario");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  if (localStorage.getItem("token") && localStorage.getItem("usuario")) {
    return <Navigate to="/nuevo-informe" replace />;
  }

  const iniciarSesion = async (e) => {
    e.preventDefault();

    setCargando(true);
    setError("");

    try {
      await login(usuario);
      navigate("/nuevo-informe");
    } catch (err) {
      setError(
        mensajeError(
          err,
          "No se pudo iniciar sesión. Verifique que el backend esté encendido."
        )
      );
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">🏛️</div>

        <h1>NAXJI</h1>

        <p className="login-subtitle">
          Copilot Generativo para la Elaboración de Informes Municipales
        </p>

        <form onSubmit={iniciarSesion}>
          <div className="form-group">
            <label>Identidad de demostración</label>

            <select
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
            >
              {USUARIOS_DEMO.map((item) => (
                <option key={item.token} value={item.token}>
                  {item.etiqueta}
                </option>
              ))}
            </select>
          </div>

          <p className="hint-text">
            El backend de PMV 1 no usa contraseña. El valor seleccionado se
            envía como token Bearer, igual que en Swagger.
          </p>

          {error && <p className="error-message">{error}</p>}

          <button className="btn-primary" type="submit" disabled={cargando}>
            {cargando ? "Ingresando..." : "Iniciar sesión"}
          </button>
        </form>

        <p className="demo-text">Acceso de demostración - PMV 1</p>
      </div>
    </div>
  );
}

export default Login;
