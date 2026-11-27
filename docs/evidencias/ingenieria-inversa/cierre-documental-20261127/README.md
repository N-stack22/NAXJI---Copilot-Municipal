# Cierre documental definitivo de ingeniería inversa

Corte **27/11/2026**, sobre la última versión de main **4f4d294f615cf0285d19f23d0f2aabbf1ee339d1**. Solo documentación y evidencias de lectura estática. No se modifica el producto, los modelos, RAG, arquitectura, plantillas, base de datos, `.env` ni el informe académico actualizado por separado.

## Entregables vigentes

- [Matriz de cumplimiento de los doce prompts](../../../INDICE_12_ENTREGABLES.md): requerimiento, entregable, evidencia, estado y observaciones, en el orden solicitado.
- [Prompt 8: reconstrucción del dominio](../analisis/dominio.md): entidades, valores/DTO, agregados observados, servicios, reglas, invariantes, estados, puertos y casos de los tres PMV, con archivos y clases reales.
- [Cinco diagramas UML textuales](../analisis/diagramas_dominio.md) y [fuentes Mermaid](../analisis/diagramas/): clases, estados de solicitud/informe/documento y secuencia de revisión.
- [Prompt 12: informe consolidado](../../../ingenieria_inversa.md), con los resultados de los doce prompts y enlaces a sus evidencias.
- [Resultados de cierre](../../../RESULTADOS_CIERRE.md), [observaciones](../../../MATRIZ_OBSERVACIONES_CIERRE.md), [ICACIT](../../../ICACIT_EVIDENCIAS.md), [alcance académico](../../../REVISION_ACADEMICA_Y_CORRECCIONES.md) y [dictamen](../../../07_auditoria_final.md).

## Correcciones contrastadas

| Observación documental | Corrección | Evidencia |
| ---| ---| ---|
| Dominio insuficientemente detallado | Se amplían clases, composición, objetos de valor, políticas, contratos, invariantes y estados; los patrones ausentes se declaran, sin implementarlos. | [Dominio](../analisis/dominio.md), [inventario de símbolos](inventario-fuente.json) |
| Revisor ambiguamente descrito como distinto del área de destino | El revisor pertenece al área de destino y debe ser distinto del creador del informe y del propietario de la solicitud. | [RevisionInformes.cargar](../../../../src/application/use_cases/revision_informes.py) |
| Numeración de prompts incoherente | Dominio pasa a Prompt 8 y variables a Prompt 5; se respeta la lista exacta de doce. | [Matriz final](../../../INDICE_12_ENTREGABLES.md) |
| Understand seguía bloqueado en encabezados individuales | Se actualiza el estado vigente: C-06 cerrada; textos anteriores se conservan bajo secciones de antecedente. | [Understand real](../../understand/README.md), [evaluación](../analisis/calidad_arquitectura.md) |
| ZAP/Linux descritos como no disponibles/no ejecutados | Se enlazan sus ejecuciones posteriores verificables, sin repetirlas. | [ZAP](../../cierre-seguridad-20261126/zap/), [CI de main 4 f 4 d 294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611) |
| Alternativas o patrones confundibles con implementación | Qdrant, TypeScript y Event-Driven separados como alternativas; eventos SQL no son broker y DTO no son entidades de dominio. | [Stack](../auditoria/stack_tecnologico.md), [dominio](../analisis/dominio.md) |
| Consolidado y referencias antiguos | Informe integrado y enlaces actuales; valoraciones e informe por corregir del antecedente quedan identificados como históricos. | [Consolidado](../../../ingenieria_inversa.md), [revisión académica vigente](../../../REVISION_ACADEMICA_Y_CORRECCIONES.md) |

## Comprobaciones de esta edición

[inventario-fuente.json](inventario-fuente.json) se obtiene con `ast.parse` sobre archivos versionados, sin importar la aplicación ni ejecutar proveedores. Enumera clases, campos, métodos y líneas. Son 110 módulos de `src`, más 2 de despliegue; el alcance de 149 archivos coincide con los propios analizados por Understand. [fuentes-sha 256.json](fuentes-sha256.json) conserva las mismas 149 huellas que [Understand](../../understand/fuentes-sha256.json).

[rutas-estaticas.json](rutas-estaticas.json) deriva decoradores y `add_api_route` del AST:42 operaciones visibles, más el alias de creación de solicitud oculto del esquema. No se presenta como un nuevo escaneo OpenAPI ni consulta productiva. Los diagramas Mermaid son reconstrucción documental manual desde esos símbolos; no son gráficos nativos de Understand.

[verificacion-documental.json](verificacion-documental.json) registra comprobación de enlaces vigentes, símbolos UML, numeración, integridad de fuentes y conservación de antecedentes. La validación no atribuye una evaluación institucional a estas comprobaciones. El diff se limita a `docs/`; los logs y gráficos originales de Understand, ZAP, carga, ML, RAG, CI y capturas no se sobrescriben.

No se repiten suites locales, análisis de Understand, escaneos ZAP ni carga 750 para cambiar documentos. La publicación activa el [workflow existente de main](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/workflows/ci.yml?query=branch%3Amain), cuyo resultado se verifica al entregar el enlace de la ejecución concreta. La [ejecución de referencia 4 f 4 d 294](https://github.com/N-stack22/NAXJI---Copilot-Municipal/actions/runs/46023410611) ya estaba a probada.

## Resultados conservados y límites

375 pruebas backend a probadas y 21 optativas omitidas;55 frontend a probadas;0 fallidas en esas suites.750 respuestas esperadas, 0 errores inesperados y 125 rechazos previstos, con dobles declarados para proveedores/decisiones humanas. ZAP ejecutado y corregido; Understand 8.1.1269 ejecutado:149 archivos, 6.719 líneas de código, 141 clases, 696 funciones, máximo ciclomático 26, SonargraphMaintainability 84,44774960712785, 423 relaciones, 0 infracciones evaluadas del núcleo y 0 errores/224 advertencias documentadas. [Cortes y evidencia original](../../../RESULTADOS_CIERRE.md).

Diez HU completas dentro del alcance académico y siete competencias ICACIT evaluadas mediante evidencia técnica. No se suman corridas, no se a prueban omitidas, no se inventan actas/encuestas/ahorro/CO₂ ni se asigna otra nota. Las limitaciones de resolución/exportación de Understand siguen explícitas; no son un bloqueo de licencia vigente.

No quedan observaciones documentales abiertas de los doce prompts en ese alcance. Las comprobaciones de operación del destino —credenciales, políticas/revocación, cookies/TLS, servicio IA estable— y la validación institucional externa permanecen fuera del cierre académico. No se simulan ni se exige modificar el producto para aparentar su ejecución.
