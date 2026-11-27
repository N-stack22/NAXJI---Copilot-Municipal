# Cierre trazable de NAXJI

Base: `d99f96088ec68f7381b143e38553a6fcce924895`. Rama local independiente; sin publicación ni despliegue.
Se leyeron los 24 documentos de referencia, el export de Trello y su captura antes de modificar el producto. Las extracciones y originales se conservan fuera del repositorio. El DOCX de evaluación coincide con su PDF salvo tres párrafos de presentación/diagramación, también revisados. Las páginas 43 y 47–52 del informe se inspeccionaron visualmente.

## Autoridad y contradicciones

| Fuente y ubicación | Decisión aplicable |
|---|---|
| Unidad III, pp. 25–28; Trello, cuatro HU PMV3 | Revisor edita/aprueba/rechaza en una sola etapa; funcionario consulta versiones/exporta Word/PDF; administrador consulta auditoría. |
| Unidad III, pp. 33–43 y 64–70 | Eventos, broker, workers, Qdrant y TypeScript son diseños documentales. La implementación que debe preservarse usa Python/FastAPI, React JSX y PostgreSQL/pgvector. |
| Unidad III, pp. 56–63 frente a pp. 27–28 | La numeración antigua de HU no coincide. Se usan los identificadores semánticos de pp. 27–28 y Trello. |
| Unidad III, pp. 45, 57–63 frente a captura de Trello | Plan original de ocho sprints frente al corte de Sprint 4/5. No se alteran fechas ni se inventan cierres del tablero. |
| Unidad III, pp. 76–84 | PoC histórica: 200 casos sintéticos, separación aproximada 140/30/30; LogisticRegression, no Random Forest. Sus métricas no representan generalización institucional. |
| Evaluación histórica del 20/11/2026, pp. 9–10, 25–28 | TR-01…TR-14 y H-01…H-20 son observaciones históricas, sujetas a comprobación actual. |
| Guías FURPS/OWASP, apartados de auditoría y parche del 13/11 | Los resultados del parche candidato no demuestran cambios en main. Se vuelven a comprobar los defectos. OWASP adoptado: Top 10:2021. |
| Cuatro prompts académicos e ICACIT | Criterios de evaluación, sin autorización para crear móviles, imágenes, biometría o nuevas funciones. |
| Unidad III, pp. 51–53, 63 y 92 | Aceptación humana, ahorro, sostenibilidad y 750 transacciones requieren medición real. No se sustituyen por porcentajes de pruebas unitarias. |

## Línea base actual

`evidencias/cierre-trazable/linea-base/checks.json` registra comandos, fecha UTC, duración y código de salida. PostgreSQL/pgvector se ejecutó en un contenedor desechable en loopback:15432. No se conectó Supabase compartido. Pytest, frontend, lint, build y diff-check terminaron con código 0. Los detalles de aprobadas/omitidas están en sus logs.

## Orden de implementación

1. PMV3: revisión por área en servidor, eventos persistentes y atómicos, historial por versión, advertencias explicadas, exportación aprobada sin IA.
2. Regresiones y defectos confirmados de PMV1/PMV2, configuración y seguridad.
3. Evaluaciones reproducibles, carga aislada y documentación de evidencias y bloqueos externos.

Los criterios sin corpus representativo, revisión humana institucional, servicio aislado o licencia se marcan parciales/bloqueados; ningún PMV se declara completo solo porque compila.
