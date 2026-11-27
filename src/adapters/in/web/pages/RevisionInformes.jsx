import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api, { mensajeError } from "../services/api";
import { obtenerUsuarioGuardado, rolesUsuario } from "../services/authService";
import FuentesInforme from "../components/FuentesInforme";
import "../styles/revision.css";

const fecha = valor => new Date(valor).toLocaleString("es-PE");
export default function RevisionInformes() {
  const [parametros, setParametros] = useSearchParams();
  const [lista, setLista] = useState([]), [historial, setHistorial] = useState(null);
  const [error, setError] = useState(""), [ocupado, setOcupado] = useState(false);
  const [versionNumero, setVersionNumero] = useState(0), [contenido, setContenido] = useState({});
  const [motivo, setMotivo] = useState(""), [comprobaciones, setComprobaciones] = useState({});
  const [pagina, setPagina] = useState(0), [recarga, setRecarga] = useState(0);
  const [auditoria, setAuditoria] = useState(null), [paginaAuditoria, setPaginaAuditoria] = useState(0);
  const usuario = obtenerUsuarioGuardado(), roles = rolesUsuario(usuario);
  const id = parametros.get("informe");
  const version = historial?.versiones.find(v => v.numero_version === versionNumero);
  const ultima = historial?.versiones.at(-1);
  const revisor = roles.includes("REVISOR") && historial?.creado_por !== usuario?.id;
  const editable = revisor && historial?.estado === "EN_REVISION" && version === ultima;
  const seccionesAdvertidas = [...new Set((version?.advertencias || []).map(a => a.seccion))];
  const comprobado = seccionesAdvertidas.every(s => comprobaciones[s]?.trim());

  useEffect(() => {
    let vigente = true;
    api.get("/revision/informes", { params: { limite: 25, desplazamiento: pagina * 25 } })
      .then(({ data }) => { if (vigente) setLista(data); })
      .catch(err => { if (vigente) setError(mensajeError(err, "No se pudo consultar el historial.")); });
    return () => { vigente = false; };
  }, [pagina, recarga]);

  useEffect(() => {
    let vigente = true;
    if (id) api.get(`/revision/informes/${id}`).then(({ data }) => {
      if (vigente) { setHistorial(data); setVersionNumero(data.versiones.at(-1)?.numero_version || 0); setComprobaciones({}); setMotivo(""); }
    }).catch(err => { if (vigente) { setHistorial(null); setError(mensajeError(err, "No se pudo abrir el informe.")); } });
    return () => { vigente = false; };
  }, [id, recarga]);

  async function ejecutar(operacion) {
    setOcupado(true); setError("");
    try { await operacion(); } catch (err) { setError(mensajeError(err, err.message || "No se pudo completar la operación.")); }
    finally { setOcupado(false); }
  }
  async function cambiar(accion, datos) {
    await ejecutar(async () => {
      await api.post(`/revision/informes/${id}/${accion}`, { numero_version: ultima.numero_version, ...datos });
      setContenido({}); setRecarga(n => n + 1);
    });
  }
  async function descargar(formato) {
    await ejecutar(async () => {
      const { data } = await api.get(`/revision/informes/${id}/versiones/${version.numero_version}/exportar`, { params: { formato }, responseType: "blob" });
      const url = URL.createObjectURL(new Blob([data]));
      const enlace = document.createElement("a"); enlace.href = url; enlace.download = `NAXJI-v${version.numero_version}.${formato}`;
      enlace.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }
  async function consultarAuditoria(paginaNueva) {
    await ejecutar(async () => {
      const { data } = await api.get("/auditoria", { params: { limite: 50, desplazamiento: paginaNueva * 50 } });
      setAuditoria(data); setPaginaAuditoria(paginaNueva);
    });
  }

  return <div className="revision-pagina">
    <h1>Revisión e historial de informes</h1>
    <p>Revise las fuentes y los hechos antes de aprobar. Cada edición guarda una nueva versión; la exportación utiliza el contenido aprobado.</p>
    {error && <div role="alert" className="revision-alerta">{error}<button type="button" onClick={() => { setError(""); setRecarga(n => n + 1); }}>Actualizar</button></div>}
    <section aria-label="Informes accesibles"><h2>Informes accesibles</h2>
      {!lista.length && <p>No hay informes accesibles en esta página.</p>}
      <ul>{lista.map(i => <li key={i.id}><button disabled={ocupado} type="button" onClick={() => { setHistorial(null); setContenido({}); setParametros({ informe: i.id }); }}>
        {i.titulo || "Informe sin título"} · {i.estado} · {fecha(i.fecha)}</button></li>)}</ul>
      <button disabled={!pagina || ocupado} onClick={() => setPagina(n => n - 1)}>Anteriores</button>
      <button disabled={lista.length < 25 || ocupado} onClick={() => setPagina(n => n + 1)}>Siguientes</button>
    </section>
    {historial && <section aria-label="Versiones guardadas"><h2>{historial.titulo || "Informe"} · {historial.estado}</h2>
      <label htmlFor="revision-version">Versión</label>
      <select id="revision-version" disabled={ocupado} value={versionNumero} onChange={e => { setVersionNumero(Number(e.target.value)); setContenido({}); setComprobaciones({}); }}>
        {historial.versiones.map(v => <option key={v.id} value={v.numero_version}>v{v.numero_version} · {fecha(v.fecha)} · Autor: {v.autor_id || "no registrado"} · {v.estado}</option>)}
      </select>
      {version && <>
        <p>Autor: {version.autor_id || "no registrado"} · Fecha: {fecha(version.fecha)} · Estado de esta versión: {version.estado}</p>
        <fieldset disabled={ocupado}>
          <legend>Contenido guardado y advertencias de respaldo</legend>
          <p>Las alertas señalan aspectos por comprobar; no verifican automáticamente la validez del documento.</p>
          {version.secciones.map(s => <div className="revision-seccion" key={s.clave}>
            <label htmlFor={`revision-${s.clave}`}>{s.titulo}</label>
            {editable ? <textarea id={`revision-${s.clave}`} rows={7} value={contenido[s.clave] ?? version.contenido[s.clave] ?? ""}
              onChange={e => setContenido(prev => ({ ...prev, [s.clave]: e.target.value }))} /> : <p className="revision-texto">{version.contenido[s.clave]}</p>}
            {version.advertencias.filter(a => a.seccion === s.clave).map((a, n) => <p className="revision-advertencia" key={n}>{a.motivo}</p>)}
          </div>)}
          <FuentesInforme sustento={version.sustento} />
          {version.advertencias.filter(a => a.seccion === "fuentes").map((a, n) => <p role="alert" key={n}>{a.motivo}</p>)}
          {editable && <>
            <button type="button" disabled={!Object.keys(contenido).length} onClick={() => cambiar("editar", { contenido: Object.fromEntries(version.secciones.map(s => [s.clave, contenido[s.clave] ?? version.contenido[s.clave] ?? ""])) })}>Guardar nueva versión de revisión</button>
            <h3>Comprobación humana</h3>
            <p>Guarde sus cambios antes de decidir. Describa qué contrastó y por qué el contenido tiene respaldo suficiente.</p>
            {seccionesAdvertidas.map(s => <label className="revision-seccion" key={s}>Justificación de {version.secciones.find(x => x.clave === s)?.titulo || s}
              <textarea maxLength={2000} value={comprobaciones[s] || ""} onChange={e => setComprobaciones(prev => ({ ...prev, [s]: e.target.value }))} /></label>)}
            <label htmlFor="revision-motivo">Motivo de la decisión</label><textarea id="revision-motivo" maxLength={4000} value={motivo} onChange={e => setMotivo(e.target.value)} />
            <button type="button" disabled={!motivo.trim() || !comprobado || Object.keys(contenido).length > 0} onClick={() => cambiar("decidir", { decision: "APROBADO", motivo, comprobaciones })}>Aprobar versión guardada</button>
            <button type="button" disabled={!motivo.trim() || Object.keys(contenido).length > 0} onClick={() => cambiar("decidir", { decision: "RECHAZADO", motivo, comprobaciones: {} })}>Rechazar versión guardada</button>
          </>}
          {historial.estado === "BORRADOR" && (roles.includes("FUNCIONARIO") || roles.includes("ADMINISTRADOR")) && <button type="button" onClick={() => cambiar("enviar", {})}>Enviar última versión a revisión</button>}
          {version.estado === "APROBADO" && ["docx", "pdf"].map(formato => <button type="button" key={formato} onClick={() => descargar(formato)}>Descargar {formato.toUpperCase()} aprobado</button>)}
        </fieldset>
        <h3>Registro de revisión</h3><ul>{historial.eventos.map(e => <li key={e.id}>{fecha(e.fecha)} · {e.accion} · {e.estado} · Usuario: {e.usuario_id || "no registrado"}{e.detalle?.motivo && ` · ${e.detalle.motivo}`}</li>)}</ul>
      </>}
    </section>}
    {roles.includes("ADMINISTRADOR") && <section aria-label="Auditoría"><h2>Auditoría</h2>
      <button disabled={ocupado} onClick={() => consultarAuditoria(0)}>Consultar auditoría</button>
      {auditoria && <><div className="revision-tabla"><table><thead><tr><th>Usuario</th><th>Acción</th><th>Informe</th><th>Fecha y hora</th></tr></thead>
        <tbody>{auditoria.map(e => <tr key={e.id}><td>{e.usuario_id || "no registrado"}</td><td>{e.accion}</td><td>{e.informe_id}</td><td>{fecha(e.fecha)}</td></tr>)}</tbody></table></div>
        {!auditoria.length && <p>No hay eventos en esta página.</p>}
        <button disabled={!paginaAuditoria || ocupado} onClick={() => consultarAuditoria(paginaAuditoria - 1)}>Eventos anteriores</button>
        <button disabled={auditoria.length < 50 || ocupado} onClick={() => consultarAuditoria(paginaAuditoria + 1)}>Más eventos</button></>}
    </section>}
  </div>;
}
