from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

from src.books.schemas import BookSchema
from src.reviews.schemas import ReviewSchema


class UserCreateSchema(BaseModel):
    username: str = Field(max_length=50)
    email: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=50, default=None)
    last_name: str = Field(max_length=50, default=None)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(max_length=50)
    email: Optional[str] = Field(max_length=50)
    password: Optional[str] = Field(min_length=8, max_length=128)
    first_name: Optional[str] = Field(max_length=50, default=None)
    last_name: Optional[str] = Field(max_length=50, default=None)


class UserSchema(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserDetailsSchema(UserSchema):
    books: List[BookSchema] = []
    reviews: List[ReviewSchema] = []


class UserLoginSchema(BaseModel):
    email: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=128)
