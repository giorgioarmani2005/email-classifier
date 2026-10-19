from fastapi import UploadFile
from core.exception import InvalidFileExtensionError, InvalidContentError
from email.policy import default
from email import message_from_bytes
from repository.uploaded import repository as uploaded_repository
from schemas.analyze import UploadedEmlRequest, AnalyzeResponse


async def upload_file(file: UploadFile):
    if file.filename.split(".")[-1] not in ["eml"]:
        raise InvalidFileExtensionError(
            "Неверное расширение файла. Допустимые расширения: .eml")
    content = await file.read()
    if not content:
        raise InvalidContentError("Файл пустой")

    msg = message_from_bytes(content, policy=default)
    body_part = msg.get_body(preferencelist=('plain', 'html'))
    if body_part:
        body_content = body_part.get_content()
        if not body_content.strip():
            raise InvalidContentError("Файл не содержит текста в теле письма")
    else:
        raise InvalidContentError("Файл не содержит тела письма")

    uploaded_repository.append(UploadedEmlRequest(
        filename=file.filename,
        from_=msg['From'],
        to_=msg['To'],
        subject=msg['Subject'],
        date=msg['Date'],
        content=body_content
    ))


async def process_text(text_request: str) -> AnalyzeResponse:
    # TODO: настоящую логику анализа обязатеьно в AIOTHRED иначе евент луп заблокируется
    return AnalyzeResponse(
        result="MOCK",
        confidence=1
    )

