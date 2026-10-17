from fastapi import APIRouter

router = APIRouter(tags=["Health Check"], prefix="/api/v1")

@router.get("/health")
def health_check():
    return {"status": "ok"}