from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from schemas.analyze import ContentRequest, UploadedEmlRequest
import services.history as history_service
import services.analyze as analyze_service
from core.exception import InvalidFileExtensionError, InvalidContentError

from api.v1.dependencies import set_cookie
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from datetime import datetime

import asyncio
from starlette.concurrency import run_in_threadpool

router = APIRouter(tags=["Analyze"], prefix="/api/v1")


@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...), client_id: str = Depends(set_cookie), session: AsyncSession = Depends(get_session)) -> dict:
    if not files:
        raise HTTPException(
            status_code=422,
            detail="Файлы не загружены",
        )
    uploaded_ids = []
    for file in files:
        try:
            id = await history_service.upload_file(file, client_id, session)
            uploaded_ids.append(id)
            # мб для фронта нужно будет id вернуть

        except InvalidFileExtensionError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e),
            )
        except InvalidContentError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла ошибка при обработке файла",
            )

    return {"status": "success",
            "message": "Файлы успешно загружены",
            "uploaded_ids": uploaded_ids
            }


@router.post("/analyze/text")
async def analyze_text(content: ContentRequest, client_id: str = Depends(set_cookie), session: AsyncSession = Depends(get_session)) -> dict:
    # TODO: logic model
    if not content.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Текст для анализа пуст",
        )
    history_id = await history_service.new_history('analyzing', content, client_id, session)

    # Я так понимаю ты тут просто зыбыл добавить run_in_threadpool. Поправь если не так
    # response = await analyze_service.process_text(content.content)
    response = await run_in_threadpool(analyze_service.process_text, content.content)

    # потом можно будет брокера подключить+celery
    await history_service.update_history_record(session, history_id,
                                                new_status='completed',
                                                new_analyzed_date=datetime.now(),
                                                new_analyzed_response=response.model_dump(mode="json"))

    return {"status": "success",
            "message": "Текст успешно проанализирован"}


@router.post("/analyze/files")
async def analyze_uploaded_files(client_id: str = Depends(set_cookie),
                                 session: AsyncSession = Depends(get_session)) -> dict:

    contents = await history_service.get_content_by_client_id(client_id, session)

    to_analyze = [
        eml for eml in contents if eml.is_eml and eml.status == 'uploaded']

    if not to_analyze:
        raise HTTPException(
            status_code=400, detail="Нет загруженных файлов для анализа")

    for eml in to_analyze:
        await history_service.update_history_record(session, eml.id, new_status='analyzing')

    tasks = [run_in_threadpool(
        analyze_service.process_text, eml.content.content) for eml in to_analyze]

    responses = await asyncio.gather(*tasks)

    # преимущества нет, один из вариантов это делать 1 коммит
    for eml, response in zip(to_analyze, responses):
        await history_service.update_history_record(
            session,
            eml.id,
            new_status='completed',
            new_analyzed_date=datetime.now(),
            new_analyzed_response=response.model_dump(mode="json")
        )

    return {
        "status": "success",
        "message": "Файлы успешно проанализированы",
        "names": [eml.content.filename for eml in to_analyze]
    }
