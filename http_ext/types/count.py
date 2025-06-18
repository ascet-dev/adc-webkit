from pydantic import BaseModel


class Count(BaseModel):
    total: int
