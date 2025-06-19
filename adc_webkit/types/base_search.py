from datetime import datetime

from .base_model import Base


class BaseSearch(Base):
    limit: int = 10
    offset: int = 0

    created_ge: datetime | None = None
    created_le: datetime | None = None

    archived: bool = False
