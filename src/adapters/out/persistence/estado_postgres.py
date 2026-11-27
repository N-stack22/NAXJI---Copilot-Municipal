from dataclasses import replace
from src.adapters.out.persistence.sql_resources import consulta


def comprobar_postgres(settings):
    with replace(settings, connect_timeout=2).connect() as c:
        return c.execute(consulta("estado_postgres", "preparacion")).fetchone()
