from fastapi import APIRouter, Depends, HTTPException
from api.v1.dependencies import set_cookie
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
import services.history as history_service
from datetime import datetime

router = APIRouter(tags=["History"], prefix="/api/v1")


@router.get("/history/{history_id}")
async def get_history(history_id: int, client_id: str = Depends(set_cookie), session: AsyncSession = Depends(get_session)) -> dict:
    analyzed_history = await history_service.get_history_by_id(history_id, client_id, session)
    if not analyzed_history:
        raise HTTPException(
            status_code=404,
            detail=f"История с id {history_id} не найдена",
        )
    return {"status": "success", "history": analyzed_history.model_dump(mode="json")}


@router.get("/histories")
async def get_histories(client_id: str = Depends(set_cookie), session: AsyncSession = Depends(get_session)) -> dict:
    histories = await history_service.get_content_by_client_id(client_id, session, sorted_field="analyzed_date")
    if not histories:
        return {"status": "success", "details": "Не было проанализировано ни одного письма", "histories_title": []}
    histories_title = [{"analyzed_date": history.analyzed_date, "id": history.id} for history in histories]

    return {"status": "success", "histories_title": histories_title}
