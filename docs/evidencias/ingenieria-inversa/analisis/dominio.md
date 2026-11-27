# Reconstrucción del dominio

Solicitud contiene valores y referencias de catálogo; Informe contiene VersionInforme; PrediccionContexto contiene NormativaPredicha; Plantilla contiene campos y una lista de SeccionSalida. Documento conserva propietario/ámbito/hash/estado y se relaciona con fragmentos. UsuarioActual es identidad con roles/área/perfil activo.

Reglas: solo el propietario o administrador elabora; contexto confirmado y obligatorios antes de generar; no sobreescribir versiones; revisor distinto del autor y del área de destino para decidir; decisiones/eventos atómicos; fuentes sujetas a acceso actual. Enumeraciones incluyen estados históricos no usados como nuevas HU. Eventos de revisión son registros inmutables del puerto nuevo, no un broker de dominio.
