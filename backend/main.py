from fastapi import FastAPI

# Хз что это, но без этого не работала апи-шка
from fastapi.middleware.cors import CORSMiddleware 
from db.config import settings

from api.v1.health import router as health_router
from api.v1.authors import router as authors_router
from api.v1.analyze import router as analyze_router
from api.v1.history import router as history_router


app = FastAPI()

# Хз что это, но без этого не работала апи-шка
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{settings.frontend_host}:{settings.frontend_port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health_router)
app.include_router(authors_router)
app.include_router(analyze_router)
app.include_router(history_router)