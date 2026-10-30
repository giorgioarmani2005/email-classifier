from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    backend_host: str
    backend_port: int
    frontend_host: str
    frontend_port: int

    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env", env_file_encoding="utf-8"
    )

    def get_postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
