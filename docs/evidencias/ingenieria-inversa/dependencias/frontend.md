# Dependencias frontend

React, React DOM, Router y Axios son dependencias de producto. Vite, plugin React, ESLint y JSDOM son herramientas de desarrollo/prueba. `package-lock.json` fija el árbol y `npm ci` se ejecutó en instalación separada de la principal.

La auditoría inicial encontró 1 alta en producción y 5 altas/3 moderadas en el árbol completo. Se aplicaron resoluciones compatibles; auditorías posteriores y `npm ci` reportaron cero avisos conocidos. SBOM npm incluye el árbol; no todas las dependencias de herramientas se ejecutan en el navegador. Ver JSON antes/después en `../../cierre-trazable/dependencias/`.
