"""Registra las versiones runtime instaladas y su SBOM, sin leer variables privadas."""
from datetime import datetime, timezone
from importlib.metadata import distribution
from pathlib import Path
from uuid import uuid4
import json
import tomllib

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]


def inventario():
    proyecto = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    pendientes = [Requirement(r) for r in proyecto["dependencies"]]
    encontrados = {}
    while pendientes:
        requisito = pendientes.pop()
        paquete = distribution(requisito.name)
        nombre = paquete.metadata["Name"]
        extras = requisito.extras or {""}
        registro = encontrados.setdefault(nombre, {"version": paquete.version, "extras": set()})
        if extras.issubset(registro["extras"]):
            continue
        if paquete.version not in requisito.specifier:
            raise ValueError("Versión instalada incompatible: " + nombre)
        registro["extras"].update(extras)
        for declaracion in paquete.requires or []:
            hijo = Requirement(declaracion)
            if not hijo.marker or any(hijo.marker.evaluate({"extra": e}) for e in registro["extras"]):
                # El marcador se evalúa en el contexto del padre, no de los extras del hijo.
                hijo.marker = None
                pendientes.append(hijo)
    return proyecto, dict(sorted(encontrados.items(), key=lambda item: item[0].lower()))


def main():
    proyecto, encontrados = inventario()
    (ROOT / "requirements-runtime.lock.txt").write_text(
        "# Resoluciones runtime instaladas; entorno Windows/Python 3.11. Validar marcadores para Linux.\n"
        + "\n".join(f'{n}=={v["version"]}' for n, v in encontrados.items()) + "\n", encoding="utf-8")
    salida = ROOT / "docs/evidencias/cierre-trazable/dependencias/sbom-python.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    sbom = {"bomFormat": "CycloneDX", "specVersion": "1.6", "serialNumber": "urn:uuid:" + str(uuid4()), "version": 1,
            "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "component": {
                "type": "application", "name": proyecto["name"], "version": proyecto["version"]}},
            "components": [{"type": "library", "name": n, "version": v["version"],
                            "purl": f'pkg:pypi/{n.lower().replace("_", "-")}@{v["version"]}'} for n, v in encontrados.items()]}
    salida.write_text(json.dumps(sbom, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventariados {len(encontrados)} paquetes runtime; no incluye herramientas QA ni certifica ausencia de vulnerabilidades.")


if __name__ == "__main__":
    main()
