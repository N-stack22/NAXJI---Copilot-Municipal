import { useEffect, useRef, useState } from "react";
import { descargarOriginal, guardarOriginal } from "../services/documentoService";
import { mensajeError } from "../services/api";

const estados = { RECUPERADO: "Fuentes recuperadas", CORPUS_VACIO: "Sin corpus procesado accesible",
  SIN_RESULTADOS: "Sin fuentes pertinentes", NO_SOLICITADO: "Sin recuperación documental" };

export default function FuentesInforme({ sustento }) {
  const [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const activo = useRef(false);
  useEffect(() => { activo.current = true; return () => { activo.current = false; }; }, []);
  const fuentes = sustento?.fuentes || [];
  const citadas = fuentes.filter(f => f.citas?.length);
  return <aside className="informe-fuentes" aria-label="Fuentes de la versión guardada">
    <h3>Fuentes de esta versión</h3>
    <p>{sustento ? estados[sustento.estado] || sustento.estado : "Versión sin fuentes documentales guardadas."}</p>
    <p>{citadas.length} fuentes citadas de {fuentes.length} recuperadas. Toda referencia requiere revisión humana.</p>
    {(!citadas.length || fuentes.some(f => f.citas?.some(c => c.estado === "TEXTO_MODIFICADO"))) &&
      <p className="warning-inline">Sustento pendiente o texto modificado: revise las afirmaciones antes de utilizar el borrador.</p>}
    {sustento?.advertencia && <p>{sustento.advertencia}</p>}
    {error && <p role="alert">{error}</p>}
    {fuentes.map((fuente, indice) => fuente.sin_acceso ? <p key={indice}>Fuente con acceso actualmente restringido.</p> :
      <details key={fuente.fragmento_id}>
        <summary>{fuente.titulo} · {fuente.citas.length ? "Citada" : "Recuperada sin citar"} · {fuente.localizacion}</summary>
        <p>Procedencia: {fuente.procedencia}</p>
        <p>Referencia: [F:{fuente.fragmento_id}] · Similitud: {fuente.similitud?.toFixed(3)}</p>
        <blockquote style={{ whiteSpace: "pre-wrap" }}>{fuente.texto}</blockquote>
        {fuente.citas.map((cita, i) => <div key={i}><p>Sección: {cita.seccion} · {cita.estado === "TEXTO_MODIFICADO" ? "Texto modificado; revisar sustento" : "Pendiente de revisión humana"}</p>
          <p style={{ whiteSpace: "pre-wrap" }}>{cita.pasaje}</p></div>)}
        <button type="button" disabled={ocupado} onClick={async () => {
          setOcupado(true); setError("");
          try {
            const blob = await descargarOriginal(fuente.documento_id);
            if (activo.current) guardarOriginal(blob, fuente.documento_id, fuente.tipo);
          } catch (err) { if (activo.current) setError(mensajeError(err, "No se pudo descargar la fuente.")); }
          finally { if (activo.current) setOcupado(false); }
        }}>Descargar original autorizado</button>
      </details>)}
  </aside>;
}
