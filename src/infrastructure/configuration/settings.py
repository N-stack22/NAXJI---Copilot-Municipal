from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    auth_mode: str = "mock"
    cors_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls):
        modo = os.getenv("NAXJI_AUTH_MODE", "mock")
        if modo not in {"mock", "disabled"}:
            raise ValueError("NAXJI_AUTH_MODE debe ser mock o disabled")
        origins = tuple(o.strip() for o in os.getenv("NAXJI_CORS_ORIGINS", "").split(",") if o.strip())
        return cls(auth_mode=modo, cors_origins=origins)
