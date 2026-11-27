from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def huella_fuentes(destino):
    archivos = [p for carpeta in ("src", "tests", "scripts", "database") for p in (ROOT/carpeta).rglob("*")
                if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".js", ".jsx", ".mjs", ".cjs", ".css", ".sql", ".json", ".joblib", ".docx"}]
    archivos += [p for p in ROOT.iterdir() if p.is_file() and
                 (p.name.startswith("requirements") or p.name in {"pyproject.toml", "package.json", "package-lock.json", "MANIFEST.in", "NAXJI_database_schema_actual.sql"})]
    huellas = {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p.read_bytes()).hexdigest() for p in sorted(archivos)}
    raw = (json.dumps(huellas, indent=2, sort_keys=True)+"\n").encode()
    (destino/"fuentes-sha256.json").write_bytes(raw)
    return sha256(raw).hexdigest()
