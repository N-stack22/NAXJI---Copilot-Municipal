import api from "./api";

export const obtenerTiposInforme = async () => {
  const response = await api.get("/tipos-informe");
  return response.data;
};

export const obtenerAreas = async () => {
  const response = await api.get("/areas");
  return response.data;
};

export const obtenerPlantillas = async (tipoInformeId) => {
  const response = await api.get("/plantillas", {
    params: {
      tipo_informe_id: tipoInformeId,
    },
  });

  return response.data;
};

export const obtenerCamposPlantilla = async (plantillaId) => {
  const response = await api.get(
    `/plantillas/${plantillaId}/campos`
  );

  return response.data;
};