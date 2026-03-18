from pydantic import BaseModel
from datetime import datetime

from typing import Generic, TypeVar, List


# Generic type variable
T = TypeVar("T")


# Model represents metadata of the file
class FileMetadata(BaseModel):
    filename:str
    size: int
    num_rows:int
    num_cols:int
    created_at:datetime


# Generic paginated response model
class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int | None = None
    limit: int
    offset: int | None = None
    next_cursor: int | None = None