# Reconstrucción del entorno

Requisitos verificados: Python 3.11, Node/npm, Docker para integración aislada y Ollama para pruebas reales. Consulte `../../../GUIA_CIERRE_Y_DEMO.md` para comandos PowerShell/Ubuntu y activación por proceso.

Prueba efectuada: build de wheel/sdist, instalación runtime en venv nuevo desde lock, instalación de wheel e importación con `-I` fuera del árbol. Se verificaron 46 recursos SQL, modelos y DOCX. El lock fue obtenido en Windows; los comandos Ubuntu son una guía preparada, no una ejecución registrada. No copie venv entre plataformas ni sustituya `.env` privados.
