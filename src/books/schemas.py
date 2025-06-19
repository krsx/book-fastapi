from pydantic import BaseModel, ConfigDict
import uuid
from datetime import date, datetime
from typing import List, Optional

from src.reviews.schemas import ReviewSchema


class BookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookDetailSchema(BookSchema):
    reviews: List[ReviewSchema]


class BookCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
