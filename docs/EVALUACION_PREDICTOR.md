# Evaluación reproducible del predictor existente

Ejecutar desde la raíz del repositorio, con el entorno ya preparado:

```bash
.venv/bin/python scripts/evaluar_predictor.py --datos /ruta/evaluacion_independiente.json --salida /ruta/resultado_nuevo.json
```

El comando usa el puerto del predictor sklearn real. No entrena, no modifica los
modelos, no invoca Ollama ni consulta Supabase. Rechaza cero casos, duplicados de
ID/asunto, etiquetas desconocidas, datos sin procedencia y archivos de salida ya
existentes. Devuelve código 2 ante entrada inválida y 0 al generar el informe.

## Archivo pendiente de suministro

Se necesita `evaluacion_independiente.json` en UTF-8 con esta estructura (los
marcadores deben sustituirse por datos y etiquetas verificadas, no por predicciones):

```json
{
  "metadata": {
    "fuente": "<identificador y procedencia del corpus>",
    "etiquetado": "<responsables, método y fecha de adjudicación de etiquetas>",
    "particion": "test",
    "independiente_entrenamiento": true
  },
  "casos": [
    {
      "id": "<identificador único seudonimizado>",
      "asunto": "<texto real autorizado para evaluación>",
      "tipo_informe": "<nombre exacto de la clase verdadera>",
      "area_destino": "<nombre exacto de la clase verdadera>",
      "temas_normativos": ["<etiqueta temática verdadera>"]
    }
  ]
}
```

Todos los casos deben tener etiquetas para las tres salidas; `temas_normativos: []`
significa ausencia de temas según el etiquetador, no etiquetas desconocidas.
No incluir secretos, datos personales innecesarios ni contenido sin autorización.
El corpus de entrenamiento, su listado de identificadores o huellas y la metodología
de partición también faltan: sin ellos no se puede comprobar solapamiento. El
programa registra la independencia **declarada**, pero siempre deja
`independencia_verificada: false`. El evaluador humano debe revisar esa evidencia.
No existe un tamaño mínimo ni umbral de rendimiento proporcionado por el profesor;
deben acordarse junto con la representatividad por clase antes de aceptar el modelo.

## Etiquetas admitidas

Tipo: `Informe Técnico`, `Informe Legal`, `Informe de Inspección`, `Memorando`.
Memorando se admite como verdad de referencia para evidenciar la carencia del
modelo: el artefacto actual no puede predecir esa clase.

Áreas:

- `Subgerencia de Ecología y Medio Ambiente`
- `Gerencia de Servicios Públicos`
- `Gerencia de Desarrollo Urbano`
- `Gerencia de Desarrollo Económico`
- `Subgerencia de Gestión del Riesgo de Desastres`
- `Oficina de Asesoría Jurídica`

Son clases de la PoC, no los nombres institucionales remapeados por PostgreSQL.
Las etiquetas temáticas exactas se obtienen del artefacto sin modificarlo:

```bash
.venv/bin/python -c 'from src.adapters.out.ai.sklearn_context_predictor import SklearnContextPredictor; print("\n".join(SklearnContextPredictor().mlb.classes_))'
```

## Resultados e interpretación

El informe JSON incluye huellas SHA-256 del corpus y de los seis archivos de
modelo/configuración, versiones de Python/numpy/sklearn, clases entrenadas, entrada,
normalización `.strip()` equivalente al caso de uso, predicciones, probabilidades,
umbral, modelo/versión y estado de validación humana pendiente. La transformación
del texto utiliza los pipelines/FeatureUnion existentes, sin sustituir vocabularios.

- Tipo y área: accuracy, precision/recall/F1 por clase, promedios macro/weighted y
  matriz de confusión. Las filas son etiquetas verdaderas y las columnas predichas.
- Temas: accuracy de conjunto exacto (todos los temas coinciden), Hamming loss
  (fracción de decisiones etiqueta/caso erróneas), precision/recall/F1 micro,
  macro, weighted y por muestra; informe por tema y matrices binarias por etiqueta
  en orden `[[TN, FP], [FN, TP]]`.
- Se incluyen las clases del catálogo, incluso sin soporte: las divisiones
  indefinidas se representan con cero. Revisar siempre `support`; el macro que
  incluye clases sin ejemplos no demuestra rendimiento sobre esas clases.
- El umbral temático continúa siendo `0.25`; las métricas evalúan las selecciones
  del predictor real con ese umbral. No se optimiza el umbral sobre el test.
- Las probabilidades por entrada no son accuracy ni prueban calibración o vigencia
  jurídica. La herramienta evalúa temas, no la validez de normas del catálogo.

Las pruebas `tests/test_evaluar_predictor.py` usan ejemplos sintéticos para comprobar
errores conocidos, cálculos, reproducibilidad y protección de archivos. Sus números
no se publican como precisión del proyecto. Las evidencias de inferencia en
`docs/evidencias/auditoria-final/predicciones_sklearn.json` tampoco contienen etiquetas
verdaderas ni métricas; son ejemplos de ejecución real del modelo.
