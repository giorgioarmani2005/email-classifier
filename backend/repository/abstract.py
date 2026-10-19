from abc import ABC, abstractmethod
from typing import Optional, List
from schemas.analyze import ContentRequest


class AbstractRepository(ABC):

    @abstractmethod
    def add_new_content(self, content: ContentRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, content_id: int) -> Optional[ContentRequest]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[ContentRequest]:
        raise NotImplementedError
