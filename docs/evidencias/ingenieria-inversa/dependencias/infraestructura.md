# Dependencias de infraestructura

PostgreSQL/pgvector se ejecutó en Docker desechable, puerto loopback 15432, rol de pruebas naxji_step3. Cada fixture creó una base aleatoria independiente. Ollama local respondió con qwen2.5:7b y bge-m3:567m en las integraciones reales.

Railway y Cloudflare Pages son destinos informados por el usuario, sin despliegue ni verificación operativa remota en esta misión. Supabase compartido no se utilizó. No se dispone de Understand/JMeter/ZAP/Sonar en PATH ni de licencia acreditada de Understand; k6 está disponible pero el ensayo de 750 se ejecutó con HTTPX/Python, sin atribuirle el nombre de otra herramienta.
