from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# El .env vive en la raiz del repositorio (dos niveles sobre este archivo).
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    database_url: str
    secret_key: str

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()
