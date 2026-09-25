import api from "./api";

const ROLES_ELABORACION = ["FUNCIONARIO", "ADMINISTRADOR"];

const ETIQUETAS_ROL = {
  FUNCIONARIO: "Funcionario municipal",
  ADMINISTRADOR: "Administrador",
  REVISOR: "Revisor",
  APROBADOR: "Aprobador",
};

export const USUARIOS_DEMO = [
  {
    token: "demo-funcionario",
    etiqueta: "Funcionario municipal",
  },
  {
    token: "demo-admin",
    etiqueta: "Administrador",
  },
  {
    token: "demo-revisor",
    etiqueta: "Revisor (solo lectura)",
  },
  {
    token: "demo-aprobador",
    etiqueta: "Aprobador (solo lectura)",
  },
  {
    token: "demo-otro",
    etiqueta: "Otro funcionario",
  },
];

const guardarUsuario = (usuario) => {
  localStorage.setItem("usuario", JSON.stringify(usuario));
};

export const login = async (token) => {
  localStorage.setItem("token", token);

  try {
    const response = await api.get("/auth/me");
    guardarUsuario(response.data);
    return response.data;
  } catch (error) {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    throw error;
  }
};

export const obtenerUsuarioActual = async () => {
  const response = await api.get("/auth/me");
  guardarUsuario(response.data);
  return response.data;
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("usuario");
};

export const obtenerUsuarioGuardado = () => {
  try {
    const raw = localStorage.getItem("usuario");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const rolesUsuario = (usuario = obtenerUsuarioGuardado()) => {
  if (!usuario?.roles) {
    return [];
  }

  if (Array.isArray(usuario.roles)) {
    return usuario.roles;
  }

  return Object.values(usuario.roles);
};

export const puedeElaborar = (usuario = obtenerUsuarioGuardado()) => {
  return rolesUsuario(usuario).some((rol) =>
    ROLES_ELABORACION.includes(rol)
  );
};

export const etiquetaUsuario = (usuario = obtenerUsuarioGuardado()) => {
  const roles = rolesUsuario(usuario);
  const rol = roles.find((item) => ETIQUETAS_ROL[item]);
  return ETIQUETAS_ROL[rol] || "Usuario de demo";
};
