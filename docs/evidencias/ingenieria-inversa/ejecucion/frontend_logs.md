# Prompt 6 — Logs frontend y alcance de las pruebas

Corte 27/11/2026, main **4f4d294**. [CI de referencia](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611):**55 pruebasfrontend a probadas, 0 fallidas, 0 omitidas**; lint y build correctos. [Extracto literal de la entregaC-06](../../understand/ci-main-extracto.log) y [logs anteriores](../../cierre-trazable/verificacion-final-05/) se conservan con su corte; no se ejecuta JSDOM otra vez para editar documentación.

`npm run test:frontend` usaNode/JSDOM;`npm run lint` ESLint y`npm run build` Vite, según [package.json](../../../../package.json). Los escenarios de sesión, documentos, revisión y avisos están en [tests/frontend](../../../../tests/frontend/). No equivalen a encuestas SUS, cookies reales entre dominios o aceptación por funcionarios.

[session.js](../../../../src/adapters/in/web/services/session.js) diferencia modo demo/Supabase, token en memoria y refresh cookie; [api.js](../../../../src/adapters/in/web/services/api.js) aplica autorización y renovación controlada. Una respuesta 403/409 prevista no es automáticamente una caída; la clasificación depende del caso de prueba ysuaserción.

La biblioteca, revisión/historial y nuevo informe son pantallas reales. El inventario de las 10 HU está en [casos_uso.md](../analisis/casos_uso.md); no se crean funciones nuevas por el número de prompts.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Logs y descubrimiento funcional frontend

La suite Node/JSDOM de final-05 aprobó 55 pruebas, incluidas tres de revisión por funcionario/revisor/administrador; lint y build terminaron con código cero. Los logs originales se conservan en `../../cierre-trazable/verificacion-final-05/`.

Rutas funcionales: login, nuevo informe en cuatro pasos, biblioteca documental y revisión/historial. Navegación protegida con perfil consultado al servidor; los controles de interfaz no sustituyen permisos backend. Se probaron carga/reintento/edición/versiones y advertencias; esta ejecución no es una prueba de cookies en navegador real ni un estudio de usabilidad con funcionarios.
