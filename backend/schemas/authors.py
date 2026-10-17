from pydantic import BaseModel


class AboutResponse(BaseModel):
    version: str
    name: str
    description: str


class AuthorsResponse(BaseModel):
    authors_names: list[str]
