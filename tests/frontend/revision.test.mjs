// Interfaz real React; HTTP simulado. Los permisos efectivos se prueban en backend/PG.
import assert from "node:assert/strict";
import test from "node:test";
import { JSDOM } from "jsdom";

for (const rol of ["REVISOR", "FUNCIONARIO", "ADMINISTRADOR"]) test(`PMV3: ${rol}, historial, advertencias y acciones`, async () => {
  const dom = new JSDOM('<div id="root"></div>', { url: "http://localhost/revision?informe=i1" });
  const previos = new Map();
  for (const clave of ["window", "document", "navigator", "HTMLElement", "Event", "localStorage", "sessionStorage"]) {
    previos.set(clave, Object.getOwnPropertyDescriptor(globalThis, clave));
    Object.defineProperty(globalThis, clave, { value: dom.window[clave], configurable: true });
  }
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  const { default: React, act } = await import("react");
  const { createRoot } = await import("react-dom/client");
  const { BrowserRouter } = await import("react-router-dom");
  const { default: axios } = await import("axios");
  const { createServer } = await import("vite");
  const vite = await createServer({ server: { middlewareMode: true, hmr: false, ws: false }, appType: "custom", optimizeDeps: { noDiscovery: true, include: [] } });
  const anteriorAdapter = axios.defaults.adapter;
  const posts = [];
  let root;
  const historial = { informe_id: "i1", creado_por: "autor", titulo: "Informe ficticio", estado: rol === "FUNCIONARIO" ? "BORRADOR" : "EN_REVISION",
    eventos: [], versiones: [{ id: "v1", numero_version: 1, autor_id: "autor", fecha: "2026-11-26T12:00:00Z", estado: "BORRADOR",
      contenido: { antecedentes: "Contenido fuente", conclusiones: "Pendiente de verificación",
        encabezado: { asunto: "Asunto que se revisa", documento: { numero: "DEMO-REV-01", emisor: "Unidad ficticia" } } },
      secciones: [{ clave: "antecedentes", titulo: "Antecedentes" }, { clave: "conclusiones", titulo: "Conclusiones" }],
      advertencias: [{ seccion: "antecedentes", motivo: "Sin cita documental accesible" }, { seccion: "conclusiones", motivo: "Dato pendiente" }] }] };
  axios.defaults.adapter = async config => {
    let data;
    if (config.url === "/auth/config") data = { mode: "mock", persistence: "memory" };
    else if (config.url === "/revision/informes") data = [{ id: "i1", titulo: historial.titulo, estado: historial.estado, fecha: historial.versiones[0].fecha }];
    else if (config.url === "/revision/informes/i1") data = structuredClone(historial);
    else if (config.url === "/auditoria") data = [{ id: "e1", usuario_id: "revisor", accion: "APROBADO", informe_id: "i1", fecha: historial.versiones[0].fecha }];
    else if (config.method === "post") {
      const body = JSON.parse(config.data); posts.push({ url: config.url, body });
      if (config.url.endsWith("/decidir")) { historial.estado = body.decision; historial.versiones[0].estado = body.decision; }
      else if (config.url.endsWith("/enviar")) historial.estado = "EN_REVISION";
      else throw new Error("Acción inesperada");
      data = structuredClone(historial);
    } else throw new Error("Petición inesperada " + config.url);
    return { data, config, status: 200, statusText: "OK", headers: {} };
  };
  try {
    sessionStorage.setItem("naxji_demo_token", "demo-funcionario");
    const sesion = await vite.ssrLoadModule("/src/adapters/in/web/services/session.js");
    sesion.saveUser({ id: rol === "FUNCIONARIO" ? "autor" : "revisor", roles: [rol] });
    const { default: Pagina } = await vite.ssrLoadModule("/src/adapters/in/web/pages/RevisionInformes.jsx");
    root = createRoot(document.getElementById("root"));
    await act(async () => root.render(React.createElement(BrowserRouter, null, React.createElement(Pagina))));
    const boton = texto => [...document.querySelectorAll("button")].find(b => b.textContent.includes(texto));
    assert.match(document.body.textContent, /Autor: autor/);
    assert.match(document.body.textContent, /Sin cita documental accesible/);
    assert.match(document.querySelector('[aria-label="Datos administrativos del documento"]').textContent, /DEMO-REV-01/);
    assert.match(document.body.textContent, /Asunto que se revisa/);
    assert.equal(document.querySelectorAll("script").length, 0);
    if (rol === "REVISOR") {
      assert.equal(boton("Aprobar versión").disabled, true);
      for (const campo of document.querySelectorAll("textarea")) {
        if (campo.id.startsWith("revision-") && campo.id !== "revision-motivo") continue;
        await act(async () => {
          Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set.call(campo, "Comprobación humana del caso ficticio");
          campo.dispatchEvent(new Event("input", { bubbles: true }));
        });
      }
      assert.equal(boton("Aprobar versión").disabled, false);
      await act(async () => boton("Aprobar versión").click());
      assert.equal(posts.length, 1);
      assert.deepEqual(Object.keys(posts[0].body.comprobaciones).sort(), ["antecedentes", "conclusiones"]);
      assert.ok(boton("Descargar PDF aprobado"));
      assert.equal(boton("Rechazar versión"), undefined);
    } else if (rol === "FUNCIONARIO") {
      assert.equal(boton("Aprobar versión"), undefined);
      await act(async () => boton("Enviar última versión").click());
      assert.equal(posts[0].body.numero_version, 1);
      assert.match(document.body.textContent, /EN_REVISION/);
    } else {
      assert.equal(boton("Aprobar versión"), undefined);
      await act(async () => boton("Consultar auditoría").click());
      assert.match(document.querySelector("table").textContent, /UsuarioAcciónInformeFecha y hora/);
      assert.match(document.querySelector("tbody").textContent, /revisorAPROBADOi1/);
    }
  } finally {
    if (root) await act(async () => root.unmount());
    axios.defaults.adapter = anteriorAdapter;
    await vite.close(); dom.window.close();
    for (const [clave, descriptor] of previos) { if (descriptor) Object.defineProperty(globalThis, clave, descriptor); else delete globalThis[clave]; }
    delete globalThis.IS_REACT_ACT_ENVIRONMENT;
  }
});
