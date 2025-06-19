from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class ReviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    rating: int = Field(lt=5)
    review_text: str
    user_uid: Optional[UUID]
    book_uid: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating: int = Field(lt=5)
    review_text: str
