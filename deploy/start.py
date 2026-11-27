"""Arranque del paquete instalado: PORT validado, sin interpolación de shell."""
import os
import uvicorn


def main():
    port = int(os.environ.get("PORT", "8000"))
    if not 1 <= port <= 65535:
        raise ValueError("PORT debe estar entre 1 y 65535")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, server_header=False,
                forwarded_allow_ips=os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1"))


if __name__ == "__main__":
    main()
