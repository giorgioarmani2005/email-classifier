from pydantic import BaseModel, EmailStr, Field, FilePath
from datetime import datetime


class ContentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50_000)


class UploadedEmlRequest(ContentRequest):
    filename: FilePath
    from_: EmailStr
    to_: EmailStr
    subject: str | None = None
    date: datetime | None = None



class AnalyzeResponse(BaseModel):
    result: str
    confidence: float
