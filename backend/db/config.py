from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent      # backend/
ENV_FILE = BASE_DIR.parent / ".env"             # корень проекта (на хосте)


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
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()