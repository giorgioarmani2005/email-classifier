from fastapi import UploadFile
from core.exception import InvalidFileExtensionError, InvalidContentError
from email.policy import default
from email import message_from_bytes
from repository.history import HistoryRepository

from schemas.analyze import UploadedEmlRequest, AnalyzeResponse, ContentRequest

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.history import HistorySchema
from datetime import datetime


async def upload_file(file: UploadFile, client_id: str, session: AsyncSession) -> int:
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

    content_request = UploadedEmlRequest(
        filename=file.filename,
        from_=msg['From'],
        to_=msg['To'],
        subject=msg['Subject'],
        date=msg['Date'],
        content=body_content
    )

    return await new_history('uploaded', content_request, client_id, session)


async def new_history(status: str, content_request: ContentRequest, client_id: str, session: AsyncSession) -> int:
    repo = HistoryRepository(session)
    return await repo.create_history(status, content_request, client_id)


async def get_content_by_client_id(client_id: str, session: AsyncSession, sorted_field: str | None = None) -> list[HistorySchema]:
    repo = HistoryRepository(session)
    histories = await repo.get_content_by_client_id(client_id, sorted_field)
    return [HistorySchema.model_validate(history) for history in histories]


async def update_history_record(session: AsyncSession, history_id: int, new_status: str | None = None, new_analyzed_date: datetime | None = None, new_analyzed_response: dict | None = None) -> None:
    repo = HistoryRepository(session)
    await repo.update_history_record(history_id, new_status, new_analyzed_date, new_analyzed_response)


async def get_history_by_id(history_id: int, client_id: str, session: AsyncSession) -> HistorySchema | None:
    repo = HistoryRepository(session)
    history = await repo.get_content_by_history_id(client_id, history_id)
    if history:
        return HistorySchema.model_validate(history)
    return None