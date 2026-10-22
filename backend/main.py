from fastapi import FastAPI
from api.v1.health import router as health_router
from api.v1.authors import router as authors_router
from api.v1.analyze import router as analyze_router
from api.v1.history import router as history_router

app = FastAPI()
app.include_router(health_router)
app.include_router(authors_router)
app.include_router(analyze_router)
app.include_router(history_router)