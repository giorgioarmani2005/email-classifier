from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Literal

from schemas.analyze import ContentRequest


class HistorySchema(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

    status: Literal['not_started', 'uploaded', 'analyzing',
                    'completed'] = Field(..., min_length=1, max_length=20)

    analyzed_date: datetime | None = Field(default=None)

    analyzed_response: dict | None = Field(default=None)

    content: ContentRequest = Field(...)

    is_eml: bool = Field(default=False)

    client_id: str = Field(...)
