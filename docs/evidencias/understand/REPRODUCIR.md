# Reproducir C-06 con Understand instalado y licenciado

Ejecutado en Windows con **8.1.1269** sobre `67d9db2f5591c1b08cb85cfe5f81dbd0ad311da9`. Mantener la base privada fuera de la carpeta publicable. No ejecutar comandos de exportación de licencia ni adjuntar configuraciones de activación.

Desde un checkout limpio del commit analizado, PowerShell:

```powershell
$repoNaxji = (Get-Location).Path
$scitoolsNaxji = 'C:\Program Files\SciTools\bin\pc-win64'
$privadoNaxji = Join-Path $env:TEMP ('naxji-understand-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $privadoNaxji | Out-Null
$baseNaxji = Join-Path $privadoNaxji 'naxji.und'
$manifiestoNaxji = Get-Content docs/evidencias/understand/alcance-archivos.json -Raw | ConvertFrom-Json
$listaNaxji = Join-Path $privadoNaxji 'archivos.txt'
$manifiestoNaxji.archivos | ForEach-Object { Join-Path $repoNaxji $_ } | Set-Content $listaNaxji -Encoding utf8
& "$scitoolsNaxji\upython.exe" -c 'import understand; print(understand.version())'
& "$scitoolsNaxji\und.exe" create -db $baseNaxji -languages Python Web -PythonUseInstalledStandard Off -PythonSetVersion Python3 -PythonImportPaths $repoNaxji
& "$scitoolsNaxji\und.exe" -db $baseNaxji add "@$listaNaxji"
& "$scitoolsNaxji\und.exe" -db $baseNaxji analyze
& "$scitoolsNaxji\upython.exe" scripts/exportar_understand.py --database $baseNaxji --repo $repoNaxji --output "$repoNaxji/docs/evidencias/understand" --und "$scitoolsNaxji/und.exe"
```

Las rutas concretas originales permanecen privadas. La lista contiene únicamente archivos propios versionados (`git ls-files src deploy index.html vite.config.js`, extensiones `.py/.js/.jsx/.css/.html`); se comprobó la correspondencia exacta con el manifiesto. `upython` es el Python provisto por Understand, no el intérprete de la aplicación. No instalar su módulo mediante pip ni cargar `.env`.

El exportador consulta métricas nativas sin redondear, escribe CSV/JSON con rutas relativas, verifica el alcance exacto, agrupa por carpetas y exporta diagramas con `Arch.draw`/`Db.draw`. Invoca la CLI real para CSV y reportes HTML/CSV/PNG. `None` permanece vacío/null y las agregaciones se identifican como tales. Un formato sin contenido gráfico no genera PNG. En los reportes de arquitectura, la portada nativa es `path_0.html`.

El log original se copia a `analisis.log` sustituyendo solo prefijos de rutas por `<REPO>` y `<SCITOOLS>`, conservando sus 224 advertencias y el resultado. No sobrescribir evidencia histórica del cierre de seguridad. Para una ejecución futura usar otro directorio, registrar el nuevo commit y volver a verificar los límites; no atribuir automáticamente estas métricas a código posterior.

El primer intento exploratorio añadió dependencias instaladas y tuvo errores de binarios externos. Se descartó para las métricas; la base definitiva se creó de cero con `UseInstalledStandard Off`. La configuración incorrecta no se mezcla con estos resultados. La opción válida para versión Python es `-PythonSetVersion Python3`; `und -version` de la guía anterior no existe en esta instalación, por eso se usa `understand.version()`.
