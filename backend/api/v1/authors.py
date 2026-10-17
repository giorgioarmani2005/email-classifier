from fastapi import APIRouter

import services.authors as authors_service
from schemas.authors import AboutResponse, AuthorsResponse



router = APIRouter(tags=["Authors"], prefix="/api/v1/authors")

@router.get("/about")
def about()-> AboutResponse:
    return authors_service.about()


@router.get("/contacts")
def contacts() -> AuthorsResponse:
    return authors_service.contacts()
