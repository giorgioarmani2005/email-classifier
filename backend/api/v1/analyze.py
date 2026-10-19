from fastapi import APIRouter, UploadFile, HTTPException, File
from schemas.analyze import ContentRequest, UploadedEmlRequest
import services.analyze as analyze_service
from core.exception import InvalidFileExtensionError, InvalidContentError


router = APIRouter(tags=["Analyze"], prefix="/api/v1")


@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)) -> dict:
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
            print(f"Unexpected error: {type(e).__name__}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла ошибка при обработке файла",
            )

    return {"status": "success",
            "message": "Файлы успешно загружены"}


@router.post("/analyze/text")
async def analyze_text(text: ContentRequest) -> dict:
    # TODO: logic model
    if not text.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Текст для анализа пуст",
        )
    await analyze_service.process_text(text.content)
    return {"status": "success",
            "message": "Текст успешно проанализирован"}


@router.post("/analyze/files")
async def analyze_uploaded_files() -> dict:
    # TODO: logic model
    contents = analyze_service.uploaded_repository.get_all()
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Нет загруженных файлов для анализа",
        )
    for content in contents:
        await analyze_service.process_text(content.content)
    
    return {"status": "success",
            "message": "Файлы успешно проанализированы",
            "names": [content.filename for content in contents if isinstance(content, UploadedEmlRequest)]
            }
