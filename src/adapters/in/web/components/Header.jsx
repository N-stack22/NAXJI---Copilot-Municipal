import { useNavigate } from "react-router-dom";

import { etiquetaUsuario, logout } from "../services/authService";

function Header() {
  const navigate = useNavigate();

  const cerrarSesion = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="header">
      <div>
        <h2>🏛️ NAXJI</h2>
        <span>Copilot Municipal</span>
      </div>

      <div className="header-user">
        <span>{etiquetaUsuario()}</span>

        <button type="button" onClick={cerrarSesion}>
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}

export default Header;
