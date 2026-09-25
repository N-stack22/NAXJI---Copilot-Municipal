import { NavLink, Outlet } from "react-router-dom";

import Header from "../components/Header";

function MainLayout() {
  return (
    <div className="app-container">
      <Header />

      <div className="main-container">
        <aside className="sidebar">
          <h3>Generación estructurada</h3>

          <NavLink
            to="/nuevo-informe"
            className={({ isActive }) =>
              isActive ? "menu-item active" : "menu-item"
            }
          >
            📄 Nuevo informe
          </NavLink>
        </aside>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;
