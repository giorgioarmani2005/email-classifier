from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime, JSON, String, CheckConstraint, Text


class History(Base):
    __tablename__ = "analyze_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "status IN ('not_started','uploaded', 'analyzing', 'completed')"),
        name='status_check',
        nullable=False,
        default="not_started"
    )
    analyzed_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True)
    analyzed_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_eml: Mapped[bool] = mapped_column(nullable=False, default=False)
    client_id: Mapped[str] = mapped_column(nullable=False, index=True)

    def __repr__(self):
        return f"<AnalyzeHistory(id={self.id}, \
        status='{self.status}', analyzed_date={self.analyzed_date}, \
        is_eml={self.is_eml}, client_id='{self.client_id}')>"
