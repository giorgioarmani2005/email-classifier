from schemas.analyze import ContentRequest, UploadedEmlRequest

#перепиши на одну бд History - статус писем: uploaded, analyzed. анонимные сессии через куки.
class ContentRepository:
    def __init__(self):
        self.repository: list[ContentRequest] = []

    def append(self, content_request: ContentRequest):
        self.repository.append(content_request)

    def find_by_filename(self, filename: str) -> ContentRequest | None:
        for content in self.repository:
            if isinstance(content, UploadedEmlRequest) and content.filename == filename:
                return content
        return None

    def get_all(self) -> list[ContentRequest]:
        return self.repository


repository = ContentRepository()
