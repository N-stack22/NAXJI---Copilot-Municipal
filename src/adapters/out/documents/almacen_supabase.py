from urllib.parse import quote, urlsplit

import httpx

from src.domain.services.errores import ErrorServicio


MIMES = {"pdf": "application/pdf", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
         "txt": "text/plain; charset=utf-8"}


class AlmacenSupabase:
    """Bucket privado existente. No crea buckets ni escribe SQL al arrancar."""
    def __init__(self, url, clave, bucket, max_bytes, transport=None):
        parsed = urlsplit(url)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username
                or parsed.password or parsed.query or parsed.fragment or not clave):
            raise ValueError("Configure URL Supabase y clave privada de Storage en el backend")
        self.url, self.clave, self.bucket = url.rstrip("/"), clave, bucket
        self.max_bytes, self.transport = max_bytes, transport

    def _client(self):
        return httpx.Client(timeout=60, transport=self.transport, trust_env=False, follow_redirects=False,
                            headers={"apikey": self.clave, "Authorization": "Bearer " + self.clave})

    def _privado(self, client):
        response = client.get(self.url + "/storage/v1/bucket/" + quote(self.bucket, safe=""))
        response.raise_for_status()
        if response.json().get("public") is not False:
            raise ValueError("Bucket público")

    def _ruta(self, ubicacion, autenticado=False):
        prefijo = "/storage/v1/object/authenticated/" if autenticado else "/storage/v1/object/"
        return self.url + prefijo + quote(self.bucket, safe="") + "/" + quote(ubicacion, safe="/")

    def guardar(self, ubicacion, contenido, tipo):
        try:
            with self._client() as client:
                self._privado(client)
                response = client.post(self._ruta(ubicacion), content=contenido,
                                       headers={"Content-Type": MIMES[tipo], "x-upsert": "true"})
                response.raise_for_status()
        except (httpx.HTTPError, ValueError, KeyError):
            raise ErrorServicio("ALMACEN_NO_DISPONIBLE", "Almacenamiento privado no disponible; reintente la carga") from None

    def leer(self, ubicacion):
        try:
            with self._client() as client:
                self._privado(client)
                with client.stream("GET", self._ruta(ubicacion, autenticado=True)) as response:
                    response.raise_for_status()
                    partes, total = [], 0
                    for parte in response.iter_bytes():
                        total += len(parte)
                        if total > self.max_bytes:
                            raise ValueError("Límite excedido")
                        partes.append(parte)
                    return b"".join(partes)
        except (httpx.HTTPError, ValueError):
            raise ErrorServicio("ALMACEN_NO_DISPONIBLE", "No se pudo leer el original privado; reintente") from None
