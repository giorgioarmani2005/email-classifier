from pydantic import BaseModel, EmailStr, Field, EmailStr, field_validator
from datetime import datetime
from email.utils import parsedate_to_datetime

class ContentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50_000)



class UploadedEmlRequest(ContentRequest):
    filename: str
    from_: EmailStr
    to_: EmailStr
    subject: str | None = None
    date: datetime | None = None

    @field_validator('date', mode='before')
    @classmethod
    def parse_email_date(cls, value):
        if isinstance(value, str):
            try:
                return parsedate_to_datetime(value)
            except Exception:
                raise ValueError("Неверный формат даты email")
        return value




class AnalyzeResponse(BaseModel):
    result: str
    confidence: float
