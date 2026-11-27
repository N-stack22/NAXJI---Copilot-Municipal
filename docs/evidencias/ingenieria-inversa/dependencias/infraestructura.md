> Actualización de cierre: los 3 PMV/10 HU están aceptados académicamente por instrucción del usuario. Este archivo conserva el corte técnico anterior. La evidencia vigente de guardias completas, ZAP real, CI y entrega Linux/Docker está en `docs/RESULTADOS_CIERRE.md`, `docs/MATRIZ_OBSERVACIONES_CIERRE.md` y `docs/INDICE_12_ENTREGABLES.md`. Understand continúa bloqueado; las omitidas no son aprobadas.

# Dependencias de infraestructura

PostgreSQL/pgvector se ejecutó en Docker desechable, puerto loopback 15432, rol de pruebas naxji_step3. Cada fixture creó una base aleatoria independiente. Ollama local respondió con qwen2.5:7b y bge-m3:567m en las integraciones reales.

Railway y Cloudflare Pages son destinos informados por el usuario, sin despliegue ni verificación operativa remota en esta misión. Supabase compartido no se utilizó. No se dispone de Understand/JMeter/ZAP/Sonar en PATH ni de licencia acreditada de Understand; k6 está disponible pero el ensayo de 750 se ejecutó con HTTPX/Python, sin atribuirle el nombre de otra herramienta.
