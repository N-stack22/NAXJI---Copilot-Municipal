import api from "./api";

export const crearSolicitud = async (datos) => {
  const response = await api.post("/solicitudes", datos);
  return response.data;
};

export const obtenerSolicitud = async (solicitudId) => {
  const response = await api.get(`/solicitudes/${solicitudId}`);
  return response.data;
};

export const actualizarSolicitud = async (solicitudId, datos) => {
  const response = await api.put(
    `/solicitudes/${solicitudId}`,
    datos
  );

  return response.data;
};

export const guardarValores = async (solicitudId, valores) => {
  const response = await api.put(
    `/solicitudes/${solicitudId}/valores`,
    {
      valores,
    }
  );

  return response.data;
};