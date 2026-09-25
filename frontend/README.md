# NAXJI — Frontend PMV 1

Este repositorio es **solo el Front-End** del Copilot Municipal.

El Back-End lo mantiene Nathalie en otro repo. No está incluido aquí y no se modifica:

https://github.com/N-stack22/NAXJI---Copilot-Municipal

## Alcance

**PMV 1 - Generación estructurada** (preparación y redacción inicial):

1. Inicio de sesión
2. Selección de tipo de informe, gerencia y plantilla
3. Registro de asunto, antecedentes y datos
4. Generación de un borrador estructurado
5. Edición y guardado

Entrega: borrador editable y almacenado con estructura institucional.

No incluye RAG, fuentes, aprobación ni exportación (PMV 2 y 3).

## Cómo correrlo

```powershell
npm install
npm run dev
```

Abra `http://localhost:5173` (o el puerto que indique Vite).

El front espera la API de Nathalie en `http://127.0.0.1:8000`. Vite reenvía `/api` a ese puerto.

Para levantar **su** backend, clone su repo en otra carpeta y siga su README. Ejemplo:

```powershell
git clone https://github.com/N-stack22/NAXJI---Copilot-Municipal.git
cd NAXJI---Copilot-Municipal
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:NAXJI_AUTH_MODE = "mock"
$env:NAXJI_CORS_ORIGINS = "http://localhost:5173"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

Si todavía no tiene el backend encendido en su PC, puede usar la API de demo local (mismo contrato PMV 1) solo para probar la interfaz:

```powershell
npm run api
```

Luego, en otra terminal: `npm run dev`.

Login de demo: **Funcionario municipal**. El backend de PMV 1 no usa contraseña; se envía el token `demo-funcionario`.
