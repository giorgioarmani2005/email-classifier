
from subprocess import Popen, run, signal, CREATE_NEW_PROCESS_GROUP
from time import sleep
from os import system, name
from sys import argv
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

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf-8")






# install postgres
# install requirements for python (pip install -r ./backend/requirements.txt)
# install requirements for python 2 (pip install -r ./frontend/requirements.txt)
# copy ./.env.example into ./.env and fill it in






system("cls" if name == "nt" else "clear")




settings = Settings()





if len(argv) > 1 and "migrate".startswith(argv[1]):
    run("alembic upgrade head", cwd="./backend")




if len(argv) > 1 and "drop".startswith(argv[1]):
    run(f'psql -U {settings.postgres_user} -c "DROP DATABASE {settings.postgres_db};"')




if len(argv) <= 1 or "run".startswith(argv[1]):
    run("py setup.py", cwd="./frontend")
    backend  = Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(settings.backend_port)], cwd="./backend", creationflags=CREATE_NEW_PROCESS_GROUP)
    frontend = Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(settings.frontend_port)], cwd="./frontend", creationflags=CREATE_NEW_PROCESS_GROUP)

    try:
        while True:
            sleep(3600)
    except KeyboardInterrupt:
        print("А всьо...")

    backend.send_signal(signal.CTRL_BREAK_EVENT)
    frontend.send_signal(signal.CTRL_BREAK_EVENT)
    backend.wait()
    frontend.wait()
