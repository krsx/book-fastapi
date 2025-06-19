from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.schemas import (
    BookDetailSchema,
    BookUpdateSchema,
    BookSchema,
    BookCreateSchema,
)
from src.db.main import get_session
from src.books.services import BookService
from src.auth.dependencies import (
    RoleChecker,
    AccessTokenBearer,
)
from src.errors import BookNotFound


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
admin_user_role = RoleChecker(["admin", "user"])


@book_router.get(
    "/", response_model=List[BookSchema], dependencies=[Depends(admin_user_role)]
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_uid}",
    response_model=List[BookSchema],
    dependencies=[Depends(admin_user_role)],
)
async def get_user_books(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_user_book(user_uid, session)
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BookSchema,
    dependencies=[Depends(admin_user_role)],
)
async def create_book(
    book_data: BookCreateSchema,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> BookSchema:
    user_id = token_details["user"]["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)

    return new_book  # type: ignore


@book_router.get("/{book_uid}", response_model=BookDetailSchema)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    dependencies=[Depends(admin_user_role)],
):
    book = await book_service.get_book(book_uid, session)
    if not book:
        raise BookNotFound()

    return book


@book_router.patch(
    "/{book_uid}", response_model=BookSchema, dependencies=[Depends(admin_user_role)]
)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateSchema,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> BookSchema:
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book is None:
        raise BookNotFound()

    return updated_book  # type: ignore


@book_router.delete(
    "/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_user_role)],
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    is_deleted = await book_service.delete_book(book_uid, session)
    if not is_deleted:
        raise BookNotFound()

    return {}
