# Aplicación de los cuatro prompts académicos

## Insumos y alcance

Se aplican `revision segun rubrica.txt`, `evaluacion integral del articulo.txt`, `trazabilidad articulo e informe.txt` y el protocolo de cuatro fases de `evaluacion de informe y articulo.docx`. Se evalúan sus consecuencias para código, resultados y evidencia. No se modifican ni publican los originales.

No se entregó un artículo científico independiente completo en inglés: Unidad III es un informe de 100 páginas con Abstract en inglés; `NAXJI_Informe_Como_Articulo.pdf` es una evaluación histórica de 31 páginas, fechada 20/11, no el artículo inglés. Por ello no se certifican corrección lingüística integral, trazabilidad entre dos manuscritos ni probabilidad de aceptación en conferencia. Los puntajes históricos no se convierten en resultados actuales.

## Prompt 1: rúbrica

Aplicación orientativa **al informe disponible y sus anexos técnicos**, no calificación oficial ni evaluación de un artículo inglés ausente. Se respetan exclusivamente las escalas 0/0,5/1 y 0/3/6.

| Criterio | Máximo | Obtenido | Justificación y corrección necesaria |
|---|---:|---:|---|
| C1 Formalidad, índice, figuras, referencias | 1 | 0,5 | Portada/figuras/referencias presentes; índice no coincide plenamente con paginación física y no se verificó toda la bibliografía. Actualizar índice/estilo/citas. |
| C2 Título/autores/resumen/objetivo/resultados | 1 | 0,5 | Componentes en informe, no estructura de paper inglés completo. Separar manuscrito científico. |
| C3 Problema/antecedentes/ingeniería/sostenibilidad | 1 | 1 | pp. 4–21 distinguen contexto, causas, ética y falta de línea base; no atribuyen ahorros no medidos. |
| C4 PMBOK/Scrum/Kanban/sprints | 1 | 0,5 | Plan y acta presentes; cortes de Trello/cronograma no acreditan cierres actuales. Adjuntar registros de ejecución reales. |
| C5 Pruebas/resultados/comparación/discusión | 1 | 0,5 | Tres antecedentes comparados y PoC; nuevos resultados locales requieren incorporarse con fecha/entorno/límites, sin mezclarlos con estudios distintos. |
| C6 Conclusiones/objetivos/PMV | 1 | 0,5 | Conclusiones históricas acotadas; actualizar con el candidato actual y bloqueos, sin declarar aceptación total. |
| C7 Evidencias funcionales/ML/repositorio/videos/Kanban | 1 | 0,5 | Pruebas y commits locales verificables; no hay nuevo video/aceptación ni publicación autorizada. |
| C8 Capas/FURPS/OWASP/Understand/reportes | 1 | 0,5 | Capas y reportes locales; Understand no disponible ni licenciado. No reemplazarlo por otra herramienta. |
| C9 Fundamentación del proyecto | 6 | 6 | Fundamentación conceptual/técnica/aplicada desarrollada; mantener alcance y limitaciones. |
| C10 Fundamentación aplicada del producto | 6 | 3 | Implementación local comprobada; integración institucional, corpus representativo y validación humana aún parciales. |
| **Total** | **20** | **13,5** | **67,5 % de esta adaptación orientativa; no nota del docente.** |

Observaciones para levantar la rúbrica: corregir exactamente los aspectos de C1/C2/C4–C8/C10 indicados. No agregar móvil/imágenes para subir puntaje. Como artículo inglés, el documento recibido queda **NO APROBADO por falta del insumo requerido**; esta decisión no niega el valor técnico del informe. La adaptación del informe requiere correcciones importantes.

## Prompt 2: revisión integral científica y lingüística

| Sección requerida | Evidencia disponible | Cumplimiento como paper inglés |
|---|---|---|
| Title | Portada p. 1 en español | No cumple el insumo completo |
| Abstract | p. 2, explícitamente acota resultados sintéticos | Cumple, calidad buena en el alcance leído |
| Keywords | p. 2 | Cumple |
| Introduction | Contexto/antecedentes pp. 4–8 en español | Parcial como estructura; inglés no evaluable |
| Related Work | Antecedentes pp. 6–8 y discusión p. 93 | Parcial; requiere síntesis de paper |
| Proposed Methodology | Diseño/Scrum/PoC | Parcial; reconciliar diseño y as-built |
| Implementation | pp. 22–44 y 85–91, más candidato local | Parcial: actualizar el corte y enlazar evidencia nueva |
| Results and Discussion | PoC/PMV y discusión | Parcial: separar ML, RAG, HTTP, aceptación y métricas históricas |
| Conclusions | p. 95 | Parcial: actualizar sin extrapolar |
| References | pp. 99–100 | Parcial: revisión bibliográfica/estilo pendiente |

Revisión lingüística limitada al Abstract realmente disponible. Ejemplos de mejora de precisión, no errores gramaticales fingidos:

| Fragmento p. 2 | Observación | Propuesta |
|---|---|---|
| “normative micro F1” | Puede sugerir validación jurídica en lugar de etiquetas temáticas | “micro-F1 for thematic regulatory labels” |
| “vector-retrieval options” | No identifica la implementación ejecutada | “PostgreSQL with pgvector for document retrieval”, conservando nota de diseño histórico |
| “both MVPs” | Remite al corte histórico del 30/10 | Mantener fecha explícita y añadir un resultado separado del candidato PMV3 del 26/11 |

No se inventan errores de gramática/voz pasiva de secciones que no existen en inglés. Arquitectura/puertos/API/web: evidencia técnica alta en laboratorio; escalabilidad media-baja por falta de proveedores productivos; dataset/proceso de entrenamiento ahora contrastados, pero generalización no demostrada. Scrum/Kanban: planificación media, cierre empírico parcial. Móvil y reconocimiento de imágenes: fuera del alcance autorizado.

Métricas disponibles: clasificación sobre test reconstruido de 30 y sondeo sintético de 60; RAG sintético y extracto MINAM; latencias/throughput HTTP de laboratorio; resultados de tests/auditorías. Faltan calidad semántica por afirmación revisada por personas, capacidad de servicios productivos, línea base municipal, aceptación y medición ambiental. Los juicios arquitectónicos 1–5 no son rendimiento medido.

La tabla /10 y el global /100 **no se calculan para el artículo inglés ausente**. Madurez del candidato: prototipo técnico con validación local. Probabilidad estadística de aceptación: no estimable a partir de estos datos. Dictamen editorial: **REQUIERE CORRECCIONES IMPORTANTES** y entrega del manuscrito inglés independiente.

## Prompt 3: trazabilidad TR-01 a TR-14

Se contrasta cada afirmación histórica con código/evidencia del candidato. «Punto» es cobertura técnico-documental adaptada: 1 respaldado en el alcance declarado, 0,5 parcial/diseño o bloqueo, 0 contradicción no corregida en el original. No mide fidelidad entre dos artículos independientes.

| TR | Fuente Unidad III (página física) | Contraste y actuación actual | Punto |
|---|---|---|---:|
| TR-01 Hexagonal | 22–24, 33–37 | Puertos/adaptadores y AST verificables; documentar relaciones reales | 1 |
| TR-02 Eventos/broker/workers | 33–43 | Propuesta; no implementados. Corregidos en documentación nueva, original pendiente | 0,5 |
| TR-03 Qdrant | 64–70 | Selección documental contradice pgvector ejecutado; original aún requiere corrección | 0 |
| TR-04 PostgreSQL/pgvector | 24, 27, 38–40 | Persistencia/recuperación real en PG aislado | 1 |
| TR-05 React TypeScript | 64, 70, 73 | React real, JSX/JS; eliminar TypeScript del as-built original | 0,5 |
| TR-06 PMV1 | 25, 85–88 | Flujo y regresiones locales; sin aceptación institucional general | 1 |
| TR-07 PMV2 | 89–91 | Carga/recuperación/citas comprobadas en alcance local; límites explicitados | 1 |
| TR-08 PMV3 | 25–28, 85–92 | Nuevo hito local de revisión/versión/auditoría/exportación; no falsear su estado histórico de octubre | 1 |
| TR-09 PoC200 | 76–84 | CSV/notebook local, partición140/30/30 y artefactos coincidentes; sin cambiar modelos | 1 |
| TR-10 Hit@1 6/6 y negativas2/2 | 90–91 | Reproducido en corpus sintético; MINAM real arroja resultados distintos y separados | 1 |
| TR-11 295/301 pruebas | 90–91 y evaluación histórica | Números históricos por commit; ejecución actual en logs separados | 1 |
| TR-12 Reducción de tiempo/error | 5–6, 95 | Metas; no hay comparación municipal antes/después | 0,5 |
| TR-13 Enlaces/videos/Trello | 96 | Referencias leídas; no validación actual completa de videos/tablero ni nueva publicación | 0,5 |
| TR-14 FURPS/OWASP/Understand/750 | 68–75, 92 | Auditorías y carga reales locales; Understand y aceptación de entorno pendientes | 0,5 |

Cobertura adaptada: **10,5/14 = 75 %**, usando el denominador explícito anterior. No es el 60,7 % histórico ni un porcentaje de trazabilidad artículo-informe. La trazabilidad bidocumental formal permanece bloqueada hasta disponer del artículo independiente.

## Prompt 4: protocolo de cuatro fases

Fase 1: adaptación orientativa 67,5 %, con las reservas anteriores; por la regla sugerida del documento (<70 %), devolver para corrección. Fase 2: revisión técnica posible, revisión integral del inglés bloqueada. Fase 3: matriz TR completada; trazabilidad entre dos manuscritos independientes bloqueada. Fase 4: **REQUIERE CORRECCIONES IMPORTANTES**. No se calcula el ponderado 40/35/25 mezclando puntuaciones adaptadas con un artículo inexistente.

## Matriz de correcciones del informe

| Página / sección exacta | Corrección a incorporar en una nueva versión del informe | Evidencia que debe enlazarse |
|---|---|---|
| 1, portada | Conciliar seis competencias con las siete de la consigna | `ICACIT_EVIDENCIAS.md` |
| 2, resumen/Abstract | Distinguir corte de octubre, evaluación del20/11 y candidato del26/11; no proclamar generalización o aprobación institucional | `RESULTADOS_CIERRE.md`, hashes y fechas |
| 3, índice | Regenerar contra la paginación física real de100 páginas | Original revisado y tabla de contenidos actualizada por sus autores |
| 20, plataformas | Reconciliar referencias OpenWebUI con React JSX actual | Inventario tecnológico/as-built |
| 22–28 y56–63, RF/HU | Unificar numeración por semántica; usar diez HU de pp27–28/Trello | `matriz_trazabilidad.md` |
| 33–43, arquitectura | Identificar eventos/broker/workers como propuesta; incluir flujo REST síncrono/puertos y transacciones | `ingenieria_inversa.md`, AST/PG |
| 37–40, modelo de datos | Distinguir tablas propuestas y esquema ejecutado; anexar migración PMV3 aditiva | SQL y pruebas de preservación |
| 43, prototipo PMV3 | Aclarar que el prototipo no obliga a dos aprobaciones; describir revisión de una etapa implementada | HU-004 original, API/GUI/pruebas |
| 45 y57–63, sprints | Registrar cortes reales frente a Trello Sprint4/5, sin inventar actas o cierres | Export/captura originales y commits locales fechados |
| 64–70, herramientas | Qdrant/TypeScript elegidos documentalmente frente a pgvector/JSX ejecutados; no migrar por coherencia aparente | Manifiestos/SQL y decisión técnica actual |
| 71–72, IA responsable | Separar citar fragmento, sustento semántico, vigencia y autorización; explicar decisión humana | Alertas/comprobaciones/eventos y protocolo de citas |
| 76–84, PoC | Añadir hashes de CSV/notebook y particiones reproducidas; LogisticRegression; 0duplicados exactos no descarta similitud/fuga | `ml/procedencia-particiones-validacion.json` |
| 82–84, métricas | Distinguir macro-F1 de3 clases entrenadas del macro sobre4 tipos de catálogo; reportar sondeo60 con límites | Evaluación ML agregada; Memorando sin clase entrenada |
| 85, matriz PMV | Añadir evidencias por cada HU/criterio, sin convertir pruebas locales en aceptación municipal | `matriz_trazabilidad.md` |
| 89–91, RAG y fuentes | Mantener resultado sintético histórico y agregar MINAM4/6 Hit@1,5/6 Hit@k,2/2 negativas; registrar MINAM-04 fallido | `rag-minam-real.json` y casos/umbrales |
| 92,750 transacciones | Reemplazar solo el estado de pendiente en el nuevo corte con logs, definiciónHTTP, concurrencia, latencias y dobles | Carga final y recursos; no mezclar con200 filas ML |
| 92, calidad | Incorporar FURPS/OWASP/SBOM actuales y ausencia de Understand; diferenciar juicios y mediciones | Informes01–07, dependencias y licencias pendientes |
| 93–95, discusión/conclusiones | Comparar constructos compatibles, conservar falta de línea base y aceptación; no extrapolar resultados sintéticos | Hallazgos abiertos y métricas actuales separadas |
| 96, enlaces | Verificar enlaces/visibilidad/autorización antes de publicar; no añadir un PR inexistente | Rama/commits locales; publicación pendiente de autorización |
| 97, feedback del experto | Mantener fecha histórica y criterios pendientes; no atribuir al experto revisiones nuevas | Registro original, sin firmas/actas nuevas |
| 99–100, bibliografía | Verificar metadatos/DOI/citas y estilo con fuentes primarias por parte de autores; no dar por validada vigencia jurídica | Revisión bibliográfica pendiente, separada de calidad de recuperación |

Prioridad: preparar artículo inglés independiente y actualizar resultados/stack; luego validar corpus y entorno institucional, fuentes por afirmación y aceptación. Las matrices técnicas están listas para revisión de los autores, sin alterar sus originales ni suplantar la evaluación docente.
