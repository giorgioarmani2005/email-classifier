

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


FRONTEND_DIR = Path(__file__).resolve().parent
BASE_DIR = FRONTEND_DIR.parent



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

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf-8")



settings = Settings()




def setup():
    with open(f"{FRONTEND_DIR}/public/js/config.js", "w") as f:
        f.write(f"let backend_host = '{settings.backend_host}';\n")
        f.write(f"let backend_port = '{settings.backend_port}';\n")

if __name__ == "__main__":
    setup()



