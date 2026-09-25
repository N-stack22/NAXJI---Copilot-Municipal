import api from "./api";

export const obtenerInforme = async (informeId) => {
  const response = await api.get(
    `/informes/${informeId}`
  );

  return response.data;
};

export const guardarBorrador = async (
  informeId,
  contenido,
  numeroVersion,
  titulo
) => {
  const response = await api.put(
    `/informes/${informeId}`,
    {
      contenido,
      numero_version: numeroVersion,
      titulo: titulo?.trim() ? titulo.trim() : null,
    }
  );

  return response.data;
};