# Prompt 3 — Dependencias frontend

Main **4f4d294**, corte 27/11/2026. [package.json](../../../../package.json) declara React, ReactDOM, ReactRouter y Axios de producto. Vite, pluginReact, ESLint, JSDOM y `@types/*` son dependencias de desarrollo. [package-lock.json](../../../../package-lock.json) fija versiones concretas; los rangos de package.json no son una medición de lo instalado en otra máquina.

Fuentes: [App.jsx](../../../../src/adapters/in/web/App.jsx), [api.js](../../../../src/adapters/in/web/services/api.js), [session.js](../../../../src/adapters/in/web/services/session.js). La interfaz está escrita en **JavaScript/JSX**, no TypeScript. La sesión Supabase usa access token en memoria y refresh mediante cookie HttpOnly del backend; no incorpora la clave privada de Storage al bundle.

Evidencia existente: [auditoría npm antes](../../cierre-trazable/dependencias/npm-completo.json), [después](../../cierre-trazable/dependencias/npm-completo-despues.json), [SBOM](../../cierre-trazable/dependencias/sbom-npm-despues.json) y [CI main 4f4d294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611):55 pruebas frontend a probadas, 0 omitidas; lint y build correctos. Son cortes fechados, no una nueva consulta de vulnerabilidades en este cierre.

`npm ci` instala desde lock; `npm run build` genera el bundle. `VITE_API_URL` se resuelve al compilar y es pública. Los paquetes `@types/react` no acreditan código TS; Qdrant y Event-Driven tampoco se añaden al frontend por figurar como alternativas evaluadas.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Dependencias frontend

React, React DOM, Router y Axios son dependencias de producto. Vite, plugin React, ESLint y JSDOM son herramientas de desarrollo/prueba. `package-lock.json` fija el árbol y `npm ci` se ejecutó en instalación separada de la principal.

La auditoría inicial encontró 1 alta en producción y 5 altas/3 moderadas en el árbol completo. Se aplicaron resoluciones compatibles; auditorías posteriores y `npm ci` reportaron cero avisos conocidos. SBOM npm incluye el árbol; no todas las dependencias de herramientas se ejecutan en el navegador. Ver JSON antes/después en `../../cierre-trazable/dependencias/`.
