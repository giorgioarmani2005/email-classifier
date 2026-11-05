

import sys
from pathlib import Path

from config import settings



FRONTEND_DIR = Path(__file__).resolve().parent

def setup():
    with open(f"{FRONTEND_DIR}/public/js/config.js", "w") as f:
        f.write(f"let backend_host = '{settings.backend_host}';\n")
        f.write(f"let backend_port = '{settings.backend_port}';\n")


if __name__ == "__main__":
    setup()
