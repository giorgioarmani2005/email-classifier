from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from schemas.analyze import ContentRequest, UploadedEmlRequest
import services.history as history_service
import services.analyze as analyze_service
from core.exception import InvalidFileExtensionError, InvalidContentError

from api.v1.dependencies import set_cookie
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from datetime import datetime

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

    response = await analyze_service.process_text(content.content)

    await history_service.update_history_record(session, history_id,
                                                new_status='completed',
                                                new_analyzed_date=datetime.now(),
                                                new_analyzed_response=response.model_dump())

    return {"status": "success",
            "message": "Текст успешно проанализирован"}


@router.post("/analyze/files")
async def analyze_uploaded_files(client_id: str = Depends(set_cookie),
                                 session: AsyncSession = Depends(get_session)) -> dict:

    contents = await history_service.get_content_by_client_id(client_id, session)

    if not contents or not any(content.is_eml and content.status == 'uploaded' for content in contents):
        raise HTTPException(
            status_code=400,
            detail="Нет загруженных файлов для анализа",
        )
    for content in contents:
        if content.is_eml and content.status == 'uploaded':
            # FIX id record
            await history_service.update_history_record(session, content.id, new_status='analyzing')

            # TODO: logic model
            response = await analyze_service.process_text(content.content)

            await history_service.update_history_record(session, content.id, new_status='completed', new_analyzed_date=datetime.now(), new_analyzed_response=response)

    return {"status": "success",
            "message": "Файлы успешно проанализированы",
            "names": [content.filename for content in contents if isinstance(content, UploadedEmlRequest)]
            }
