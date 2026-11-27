# Prompt 10 — Evaluación arquitectónica vigente

Main **4f4d294**, corte 27/11/2026. **Understand ejecutado, C-06 cerrada.** [Resumen original](../../understand/resumen.json), [configuración](../../understand/configuracion.json), [log](../../understand/analisis.log), [CSV/HTML/diagramas](../../understand/README.md). No se recalculan métricas ni puntuaciones con esta revisión documental.

| Criterio | Evidencia real | Interpretación y límites |
| ---| ---| ---|
| Complejidad | 149 archivos propios, 6.719 líneas de código, 141 clases, 696 funciones; máximo ciclomático 26 | 26 en ExportadorDocx.exportar; no de muestra un fallo funcional ni autoriza refactorizar PMV/modelos. |
| Mantenibilidad | SonargraphMaintainability 84,44774960712785, implementación ML 2 de Understand | Métrica de dependencias, no porcentaje de calidad institucional. Halstead global no disponible; valores por archivo conservados, ceros/null distinguidos. |
| Acoplamiento y capas | 423 relaciones propias, 0 infracciones evaluadas del núcleo; [CSV](../../understand/dependencias-rutas.csv) | Solo dependencias resueltas; no modela HTTP dinámico. Acoplamiento de clases/fan-in/fan-out disponibles enCSV, no inventar umbral global. |
| Cohesión/testeabilidad | Puertos/casos por responsabilidad, inyección y guardias; 375 backend/21 omitidas, 55 frontend | No equivale a un índice numérico de cohesión, ni encuesta de usabilidad. |
| Fiabilidad/seguridad | Atomicidad/versiones/permisos enPG; [ZAP antes/después](../../cierre-seguridad-20261126/zap/) | Sin altas/medias/bajas posteriores en los objetivos locales analizados; informativos y alcance conservados. |
| Rendimiento | [750 HTTP](../../cierre-seguridad-20261126/carga-750-final/resultado.json), 0 fallos inesperados | Dobles declarados para Auth/Storage/LLM/embeddings/decisión humana; no mide capacidad IA productiva. |
| Entrega | [CI 4 f 4 d 294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611), wheel/sdist, Docker Linux | No despliegue ni validación institucional externa. |

Understand termina **0 errores/224 advertencias**: bibliotecas excluidas y una referencia absoluta de Vite no resuelta desde HTML, aunque main.jsx se analiza. Sus limitaciones nativas de exportación están documentadas: CSV de arquitectura personalizada y detalles HTML no generados. Se conserva el original y la vista derivada se identifica como tal.

Los juicios 1–5 del antecedente son valoraciones históricas, no métricas de Understand ni puntuaciones nuevas. No se inventa un promedio de calidad ni se declara mantenibilidad total a partir de un valor.

## Antecedente literal conservado de 4f4d294

Texto heredado, anterior a esta revisión documental del 27/11/2026. Las referencias a Understand bloqueado, ausencia de ZAP o falta de validación Linux describen aquel diagnóstico; quedan superadas por las evidencias vigentes enlazadas arriba. Los logs y mediciones originales no se alteran.

> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Evaluación arquitectónica

Valoraciones cualitativas 1–5 según el prompt, no medidas de desempeño: 1 débil, 3 parcial, 5 evidencia completa en lo inspeccionado.

| Criterio | Juicio | Evidencia / límite |
|---|---|---|
| Cohesión | 4 | Casos/puertos por responsabilidad; formulario principal aún extenso |
| Acoplamiento | 3 | Dominio/aplicación aislados por AST; configuración/provider wiring relacionados |
| Escalabilidad | 2 | SQL exacto y tareas IA síncronas; sin ensayo de proveedores productivos |
| Mantenibilidad | 4 | SQL recursos, manifest canónico, snapshots y pruebas; dependencia de formatos/modelos versionados |
| Testeabilidad | 4 | Dobles inyectables y PG/Ollama opt-in reales; Supabase real pendiente |
| Seguridad | 3 | Permisos, TLS, hashes, no-store y controles locales; RLS operativo/alertas/quotas pendientes |

No se convierte la media de estos juicios en un porcentaje de calidad. Understand no se ejecutó ni se sustituye por este análisis.
