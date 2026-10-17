from schemas.authors import AboutResponse, AuthorsResponse


def about() -> AboutResponse:
    return AboutResponse(
        version="1.0.0",
        name="Email Classifier",
        description="A service that classifies emails with machine learning."
    )


def contacts() -> AuthorsResponse:
    return AuthorsResponse(
        authors_names=[
            "Giorgio Studenko",
            "Andrew Abrosimov",
            "Ivan Jivov",
            "Yulia Rodnova",
        ]
    )
