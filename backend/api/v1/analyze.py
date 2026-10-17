from fastapi import APIRouter, UploadFile, HTTPException
from schemas.analyze import ContentRequest
import services.analyze as analyze_service
from core.exception import InvalidFileExtensionError, InvalidContentError


router = APIRouter(tags=["Analyze"], prefix="/api/v1")


@router.post("/upload")
async def upload_files(files: list[UploadFile]) -> dict:
    if not files:
        raise HTTPException(
            status_code=422,
            detail="Файлы не загружены",
        )
    for file in files:
        try:
            await analyze_service.upload_file(file)

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
            raise HTTPException(
                status_code=500,
                detail="Произошла ошибка при обработке файла",
            )

    return {"status": "success",
            "message": "Файлы успешно загружены"}


@router.post("/analyze/text")
async def analyze_text(text: ContentRequest) -> dict:
    # TODO: logic model
    await analyze_service.process_text(text.content)
    return {"status": "success",
            "message": "Текст успешно проанализирован"}


@router.get("/analyze/files")
async def analyze_uploaded_files(files: list[UploadFile]) -> dict:
    # TODO: logic model
    for file in files:
        await analyze_service.process_uploaded_file(file)
    return {"status": "success",
            "message": "Файлы успешно проанализированы"}
