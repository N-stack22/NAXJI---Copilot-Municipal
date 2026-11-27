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
