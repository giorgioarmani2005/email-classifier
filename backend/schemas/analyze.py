from pydantic import BaseModel, EmailStr, Field, EmailStr, field_validator, ConfigDict
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List


class ContentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50_000)


class UploadedEmlRequest(ContentRequest):
    model_config = ConfigDict(populate_by_name=True)
    filename: str
    from_: EmailStr = Field(alias='from')
    to_: EmailStr = Field(alias='to')
    subject: str | None = None
    date: datetime | None = None

    @field_validator('date', mode='before')
    @classmethod
    def parse_email_date(cls, value):
        if isinstance(value, str):
            try:
                return parsedate_to_datetime(value)
            except Exception:
                return value
        return value


class AnalyzeResponse(BaseModel):
    triage: str | None = None
    triage_confidence: float | None = None
    priority: str | None = None
    priority_confidence: float | None = None
    risk: str | None = None
    risk_confidence: float | None = None
    should_process: str | None = None
    should_process_confidence: float | None = None
    shap_indices: List[int] | None = None