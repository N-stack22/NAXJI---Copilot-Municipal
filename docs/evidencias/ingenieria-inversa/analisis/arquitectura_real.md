# Flujo arquitectónico real

React → API → caso de uso → dominio/puertos → adaptadores → PG/Ollama/Storage/exportación. Container hace la composición. Pruebas AST verifican que dominio/aplicación no importen infraestructura/frameworks.

Las reservas desacoplan inferencia de bloqueos largos, pero HTTP sigue siendo síncrono. Finalizar un índice usa bloqueo por intento y una transacción; buscar filtra el corpus autorizado antes de ordenar/limitar. PMV3 bloquea la versión vigente y confirma decisión/evento juntos. Se comprobó concurrencia entre instancias y rollback cuando falla el evento. No se encontraron broker, workers, Qdrant o TypeScript; esos elementos del informe requieren corrección documental.
