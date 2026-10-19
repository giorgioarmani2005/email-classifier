from schemas.analyze import ContentRequest, UploadedEmlRequest
from repository.abstract import AbstractRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from models.history import History

from datetime import datetime


class HistoryRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_history(self, status: str, content_request: ContentRequest, client_id: str) -> int:
        try:
            src_data = content_request.model_dump()

            history = History(
                status=status,
                analyzed_date=None,
                analyzed_response=None,
                content=src_data,
                is_eml=isinstance(content_request, UploadedEmlRequest),
                client_id=client_id
            )
            self.session.add(history)
            await self.session.commit()
            await self.session.refresh(history)
            return history.id

        except Exception as e:
            self.session.rollback()
            raise e

    async def get_content_by_client_id(self, client_id: str) -> list[History]:
        query = select(History).where(History.client_id == client_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_history_record(self, history_id: int, new_status: str | None = None, new_analyzed_date: datetime | None = None, new_analyzed_response: dict | None = None) -> None:

        update_data = {}
        if new_status is not None:
            update_data["status"] = new_status
        if new_analyzed_date is not None:
            update_data["analyzed_date"] = new_analyzed_date
        if new_analyzed_response is not None:
            update_data["analyzed_response"] = new_analyzed_response

        stmt = (
            update(History)
            .where(History.id == history_id)
            .values(
                **update_data
            )
            .execution_options(synchronize_session=False)
        )
        await self.session.execute(stmt)
        await self.session.commit()
