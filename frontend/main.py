
from setup import setup

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent
PUBLIC = FRONTEND_DIR / "public"

setup()

app = FastAPI()

@app.get("/{path:path}")
async def _(path: str) -> FileResponse:
    if not path:
        return FileResponse(PUBLIC / "index.html")
    
    file = (PUBLIC / path).resolve()

    if file.is_relative_to(PUBLIC.resolve()) and file.is_file():
        return FileResponse(file)

    return FileResponse(PUBLIC / "404.html", status_code=404)

