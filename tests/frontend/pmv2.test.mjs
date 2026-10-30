import assert from "node:assert/strict";
import test from "node:test";
import { JSDOM } from "jsdom";

test("gestión documental: carga, error recuperable, reintento y fuentes por versión", async () => {
  const dom = new JSDOM('<div id="root"></div>', { url: "http://localhost/nuevo-informe" });
  const anteriores = new Map();
  for (const key of ["window", "document", "navigator", "HTMLElement", "Event", "localStorage", "sessionStorage"]) {
    anteriores.set(key, Object.getOwnPropertyDescriptor(globalThis, key));
    Object.defineProperty(globalThis, key, { value: dom.window[key], configurable: true });
  }
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  const { default: React, act } = await import("react");
  const { createRoot } = await import("react-dom/client");
  const { default: axios } = await import("axios");
  const { createServer } = await import("vite");
  const vite = await createServer({ server: { middlewareMode: true, hmr: false, ws: false }, appType: "custom",
    optimizeDeps: { noDiscovery: true, include: [] } });
  const adapterAnterior = axios.defaults.adapter;
  let root;
  let fallar = true, llamadasProcesar = 0, cargas = 0;
  const doc = { id: "d1", usuario_id: "u1", titulo: "Manual ambiental", procedencia: "Fuente ficticia", ambito: "PRIVADO",
    nombre_original: "manual.txt", estado: "CARGADO", fragmentos: 0 };
  axios.defaults.adapter = async config => {
    let data;
    if (config.url === "/auth/config") data = { mode: "mock", persistence: "memory" };
    else if (config.url === "/documentos/configuracion") data = { habilitado: true, formatos: ["txt", "pdf", "docx"], max_bytes: 10485760 };
    else if (config.url === "/documentos" && config.method === "get") data = [];
    else if (config.url === "/documentos" && config.method === "post") {
      cargas++;
      assert.ok(config.data instanceof FormData);
      assert.equal(config.data.get("titulo"), "Manual ambiental");
      assert.equal(config.data.get("procedencia"), "Fuente autorizada ficticia");
      data = { ...doc };
    } else if (config.url === "/documentos/d1/procesar") {
      llamadasProcesar++;
      if (fallar) throw Object.assign(new Error("Embeddings caídos"), { config, response: { status: 503, data: { detail: "Embeddings caídos; reintente" } } });
      data = { ...doc, estado: "INDEXADO", fragmentos: 1 };
    } else throw new Error("Petición inesperada " + config.url);
    return { data, config, status: 200, statusText: "OK", headers: {} };
  };
  try {
    sessionStorage.setItem("naxji_demo_token", "demo-funcionario");
    const { default: Documentos } = await vite.ssrLoadModule("/src/adapters/in/web/components/DocumentosInforme.jsx");
    const { default: Fuentes } = await vite.ssrLoadModule("/src/adapters/in/web/components/FuentesInforme.jsx");
    const sesion = await vite.ssrLoadModule("/src/adapters/in/web/services/session.js");
    sesion.saveUser({ id: "u1", roles: ["FUNCIONARIO"] });
    root = createRoot(document.getElementById("root"));
    const render = async componente => { await act(async () => root.render(componente)); };
    const pulsar = async texto => {
      const boton = [...document.querySelectorAll("button")].find(b => b.textContent.includes(texto));
      assert.ok(boton && !boton.disabled, texto);
      await act(async () => boton.click());
    };
    const escribir = async (id, valor) => act(async () => {
      const input = document.getElementById(id);
      Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set.call(input, valor);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    await render(React.createElement(Documentos, { usarDocumentos: true, onChange() {}, puedeCargar: true }));
    await pulsar("Gestionar documentos");
    assert.match(document.body.textContent, /No hay documentos visibles/);
    await escribir("documento-titulo", "Manual ambiental");
    await escribir("documento-procedencia", "Fuente autorizada ficticia");
    const input = document.getElementById("documento-archivo");
    Object.defineProperty(input, "files", { value: [new File(["Referencia municipal"], "manual.txt", { type: "text/plain" })] });
    await act(async () => input.dispatchEvent(new Event("change", { bubbles: true })));
    await act(async () => document.querySelector("form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true })));
    assert.equal(cargas, 1);
    assert.match(document.body.textContent, /CARGADO/);
    await pulsar("Procesar documento");
    assert.match(document.body.textContent, /Embeddings caídos/);
    assert.equal(document.getElementById("documento-titulo").value, "Manual ambiental");
    fallar = false;
    await pulsar("Procesar documento");
    assert.equal(llamadasProcesar, 2);
    assert.match(document.body.textContent, /INDEXADO/);
    const sustento = { estado: "RECUPERADO", fuentes: [{ documento_id: "d1", fragmento_id: "f1", titulo: doc.titulo,
      procedencia: doc.procedencia, texto: "Texto exacto de referencia <script>no ejecutar</script>",
      localizacion: "Párrafo 2", similitud: .88, citas: [{ seccion: "conclusiones", pasaje: "Pasaje guardado", estado: "TEXTO_MODIFICADO" }] },
      { documento_id: "d2", fragmento_id: "f2", titulo: "Otra fuente", texto: "Otro texto", localizacion: "Página 1", citas: [] }] };
    await render(React.createElement(Fuentes, { sustento }));
    assert.match(document.body.textContent, /1 fuentes citadas de 2 recuperadas/);
    assert.match(document.body.textContent, /Texto modificado; revisar sustento/);
    assert.match(document.body.textContent, /Recuperada sin citar/);
    assert.equal(document.querySelector("script"), null);
    await render(React.createElement(Fuentes, { sustento: null }));
    assert.match(document.body.textContent, /Versión sin fuentes documentales guardadas/);
  } finally {
    if (root) await act(async () => root.unmount());
    axios.defaults.adapter = adapterAnterior;
    await vite.close(); dom.window.close();
    for (const [key, descriptor] of anteriores) {
      if (descriptor) Object.defineProperty(globalThis, key, descriptor); else delete globalThis[key];
    }
    delete globalThis.IS_REACT_ACT_ENVIRONMENT;
  }
});
