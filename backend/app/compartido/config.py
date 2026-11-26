from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# El .env vive en la raiz del repositorio (tres niveles sobre este archivo).
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    # Origenes del frontend permitidos. En .env se escribe como lista JSON.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()
