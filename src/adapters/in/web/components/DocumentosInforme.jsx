import { useEffect, useRef, useState } from "react";
import { mensajeError } from "../services/api";
import { obtenerUsuarioGuardado } from "../services/authService";
import { cargarDocumento, configuracionDocumentos, descargarOriginal, guardarOriginal,
  listarDocumentos, procesarDocumento } from "../services/documentoService";

export default function DocumentosInforme({ usarDocumentos, onChange, disabled, puedeCargar, mostrarSeleccion = true }) {
  const [abierto, setAbierto] = useState(false);
  const [documentos, setDocumentos] = useState([]);
  const [config, setConfig] = useState(null);
  const [datos, setDatos] = useState({ titulo: "", procedencia: "", ambito: "PRIVADO" });
  const [archivo, setArchivo] = useState(null);
  const [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [aviso, setAviso] = useState("");
  const [hayMas, setHayMas] = useState(false);
  const activo = useRef(false), trabajando = useRef(false);
  const inputArchivo = useRef(null);
  useEffect(() => { activo.current = true; return () => { activo.current = false; }; }, []);
  const admin = obtenerUsuarioGuardado()?.roles?.includes("ADMINISTRADOR");

  async function ejecutar(tarea) {
    if (trabajando.current) return;
    trabajando.current = true;
    setOcupado(true); setError(""); setAviso("");
    try { await tarea(); }
    catch (err) { if (activo.current) setError(mensajeError(err, "No se pudo completar la operación documental.")); }
    finally { trabajando.current = false; if (activo.current) setOcupado(false); }
  }
  async function actualizar() {
    const configuracion = await configuracionDocumentos();
    if (!activo.current) return;
    setConfig(configuracion);
    if (!configuracion.habilitado) return;
    const lista = await listarDocumentos();
    if (activo.current) { setDocumentos(lista); setHayMas(lista.length === 100); }
  }
  function abrir() {
    setAbierto(true);
    ejecutar(actualizar);
  }
  function cargar(evento) {
    evento.preventDefault();
    if (!archivo) { setError("Seleccione un archivo."); return; }
    if (config && archivo.size > config.max_bytes) { setError("El archivo supera el límite de tamaño."); return; }
    ejecutar(async () => {
      const doc = await cargarDocumento({ ...datos, archivo });
      if (!activo.current) return;
      setDocumentos(prev => [doc, ...prev.filter(d => d.id !== doc.id)]);
      setArchivo(null);
      if (inputArchivo.current) inputArchivo.current.value = "";
      setAviso("Documento guardado. Procéselo para incorporarlo a la recuperación.");
    });
  }
  return <section className="informe-documentos" aria-label="Documentos de referencia">
    <h3>Documentos de referencia</h3>
    {mostrarSeleccion && <label><input type="checkbox" checked={usarDocumentos} disabled={disabled || !puedeCargar}
      onChange={e => onChange(e.target.checked)} /> Elaborar con documentos autorizados</label>}
    <p>Se buscarán fuentes pertinentes entre los documentos procesados a los que tiene acceso. No acreditan inspecciones ni hechos del caso.</p>
    {!abierto ? <button type="button" className="btn-secondary" disabled={disabled} onClick={abrir}>Gestionar documentos</button> : <>
      <button type="button" className="btn-secondary" disabled={ocupado || disabled}
        onClick={() => ejecutar(actualizar)}>Actualizar documentos</button>
      {ocupado && <p role="status">Procesando solicitud documental…</p>}
      {error && <p role="alert" className="error-message">{error}</p>}
      {aviso && <p role="status">{aviso}</p>}
      {config && !config.habilitado && <p role="status">Gestión documental pendiente de activación en el servidor. Revise la guía PMV2.</p>}
      {config?.habilitado && <>
        <p>Formatos: {config.formatos.join(", ").toUpperCase()} · Máximo {(config.max_bytes / 1048576).toFixed(0)} MB. Los PDF escaneados necesitan OCR externo.</p>
        {puedeCargar && <form onSubmit={cargar}>
          <fieldset disabled={ocupado || disabled}>
            <legend>Incorporar documento autorizado</legend>
            <label htmlFor="documento-titulo">Título del documento *</label>
            <input id="documento-titulo" required maxLength={250} value={datos.titulo}
              onChange={e => setDatos(prev => ({ ...prev, titulo: e.target.value }))} />
            <label htmlFor="documento-procedencia">Procedencia y autorización de uso *</label>
            <input id="documento-procedencia" required maxLength={1000} value={datos.procedencia}
              onChange={e => setDatos(prev => ({ ...prev, procedencia: e.target.value }))} />
            <label htmlFor="documento-ambito">Acceso</label>
            <select id="documento-ambito" value={datos.ambito} onChange={e => setDatos(prev => ({ ...prev, ambito: e.target.value }))}>
              <option value="PRIVADO">Privado: propietario y administrador</option>
              <option value="AREA">Mi área</option>
              {admin && <option value="INSTITUCIONAL">Institucional</option>}
            </select>
            <label htmlFor="documento-archivo">Archivo *</label>
            <input id="documento-archivo" type="file" required ref={inputArchivo}
              accept={config.formatos.map(f => `.${f}`).join(",")} onChange={e => setArchivo(e.target.files[0] || null)} />
            <button className="btn-primary" type="submit">Cargar documento</button>
          </fieldset>
        </form>}
        {!documentos.length && <p>No hay documentos visibles. Cargue y procese una fuente autorizada.</p>}
        <ul>{documentos.map(doc => <li key={doc.id}>
          <details><summary>{doc.titulo} · {doc.estado} · {doc.fragmentos} fragmentos</summary>
            <p>{doc.procedencia} · Acceso {doc.ambito} · {doc.nombre_original}</p>
            <p>{doc.error || "Sin errores registrados"}</p>
            {puedeCargar && (admin || doc.usuario_id === obtenerUsuarioGuardado()?.id) &&
              <button type="button" disabled={ocupado || disabled || ["SUBIENDO", "ERROR_CARGA"].includes(doc.estado)}
                onClick={() => ejecutar(async () => {
                  const actualizado = await procesarDocumento(doc.id);
                  if (activo.current) setDocumentos(prev => prev.map(d => d.id === doc.id ? actualizado : d));
                })}>{doc.estado === "ERROR_PROCESAMIENTO" || doc.estado === "PROCESANDO" ? "Reintentar procesamiento" : "Procesar documento"}</button>}
            <button type="button" disabled={ocupado || disabled} onClick={() => ejecutar(async () => {
              const blob = await descargarOriginal(doc.id);
              if (activo.current) guardarOriginal(blob, doc.id, doc.tipo);
            })}>Descargar original</button>
          </details>
        </li>)}</ul>
        {hayMas && <button type="button" disabled={ocupado || disabled} onClick={() => ejecutar(async () => {
          const siguientes = await listarDocumentos({ params: { offset: documentos.length } });
          if (activo.current) {
            setDocumentos(prev => [...prev, ...siguientes.filter(d => !prev.some(p => p.id === d.id))]);
            setHayMas(siguientes.length === 100);
          }
        })}>Ver más documentos</button>}
        <p>Si la carga falló, vuelva a enviar el mismo archivo; se conserva su identificador.</p>
      </>}
    </>}
  </section>;
}
