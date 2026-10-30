import api from "./api";

export const configuracionDocumentos = async (opciones = {}) =>
  (await api.get("/documentos/configuracion", opciones)).data;
export const listarDocumentos = async (opciones = {}) =>
  (await api.get("/documentos", opciones)).data;
export const cargarDocumento = async ({ archivo, titulo, procedencia, ambito }) => {
  const datos = new FormData();
  datos.append("archivo", archivo);
  datos.append("titulo", titulo);
  datos.append("procedencia", procedencia);
  datos.append("ambito", ambito);
  return (await api.post("/documentos", datos, { headers: { "Content-Type": undefined } })).data;
};
export const procesarDocumento = async id =>
  (await api.post(`/documentos/${id}/procesar`)).data;
export const descargarOriginal = async id => {
  try {
    return (await api.get(`/documentos/${id}/original`, { responseType: "blob" })).data;
  } catch (error) {
    if (error.response?.data instanceof Blob) {
      try { error.response.data = JSON.parse(await error.response.data.text()); } catch { /* error público genérico */ }
    }
    throw error;
  }
};
export function guardarOriginal(blob, id, tipo = "bin") {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = `NAXJI-fuente-${id}.${tipo}`;
  enlace.click();
  URL.revokeObjectURL(url);
}
