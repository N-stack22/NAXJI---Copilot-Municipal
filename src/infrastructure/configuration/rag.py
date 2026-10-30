from dataclasses import dataclass


@dataclass(frozen=True)
class RagSettings:
    enabled: bool = False
    max_bytes: int = 10 * 1024 * 1024
    formats: tuple[str, ...] = ("pdf", "docx", "txt")
    chunk_size: int = 1200
    chunk_overlap: int = 180
    max_chunks: int = 2000
    top_k: int = 6
    threshold: float = 0.5
    context_chars: int = 8000
    lease_seconds: int = 1800
    processing_revision: str = "1"
    embedding_model: str = "bge-m3:567m"
    embedding_dimension: int = 1024
    embedding_timeout: int = 120
    storage_bucket: str = "naxji-documentos"

    def __post_init__(self):
        if not (100 <= self.chunk_size <= 6000 and 0 <= self.chunk_overlap < self.chunk_size):
            raise ValueError("Segmentación RAG inválida")
        if not (1 <= self.max_bytes <= 50 * 1024 * 1024 and 1 <= self.max_chunks <= 5000):
            raise ValueError("Límites documentales inválidos")
        if not (1 <= self.top_k <= 30 and -1 <= self.threshold <= 1
                and self.chunk_size <= self.context_chars <= 40000):
            raise ValueError("Límites de recuperación inválidos")
        if self.embedding_dimension != 1024:
            raise ValueError("Esta migración usa vector(1024); cambiar dimensión requiere migración e índice nuevos")
        if not (1 <= self.embedding_timeout <= 300 and 60 <= self.lease_seconds <= 7200):
            raise ValueError("Tiempos RAG inválidos")
        if not self.processing_revision or not self.embedding_model.strip() or not self.storage_bucket.strip():
            raise ValueError("Modelo, revisión y bucket RAG requeridos")
        if not self.formats or set(self.formats) - {"pdf", "docx", "txt"}:
            raise ValueError("Formatos RAG inválidos")

    @classmethod
    def from_values(cls, values):
        def entero(key, default):
            return int(values.get("NAXJI_" + key, default))
        enabled = values.get("NAXJI_RAG_ENABLED", "false").lower()
        if enabled not in {"true", "false"}:
            raise ValueError("NAXJI_RAG_ENABLED debe ser true o false")
        return cls(enabled=enabled == "true", max_bytes=entero("DOCUMENT_MAX_BYTES", 10485760),
                   formats=tuple(v.strip() for v in values.get("NAXJI_DOCUMENT_FORMATS", "pdf,docx,txt").split(",")),
                   chunk_size=entero("RAG_CHUNK_SIZE", 1200), chunk_overlap=entero("RAG_CHUNK_OVERLAP", 180),
                   max_chunks=entero("RAG_MAX_CHUNKS", 2000), top_k=entero("RAG_TOP_K", 6),
                   threshold=float(values.get("NAXJI_RAG_MIN_SIMILARITY", "0.5")),
                   context_chars=entero("RAG_CONTEXT_CHARS", 8000), lease_seconds=entero("RAG_LEASE_SECONDS", 1800),
                   processing_revision=values.get("NAXJI_RAG_PROCESSING_REVISION", "1"),
                   embedding_model=values.get("NAXJI_EMBEDDING_MODEL", "bge-m3:567m"),
                   embedding_dimension=entero("EMBEDDING_DIMENSION", 1024),
                   embedding_timeout=entero("EMBEDDING_TIMEOUT_SECONDS", 120),
                   storage_bucket=values.get("NAXJI_STORAGE_BUCKET", "naxji-documentos"))
