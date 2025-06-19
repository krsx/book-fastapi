import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from datetime import datetime

from src.db.models import Book
from src.books.schemas import BookCreateSchema, BookUpdateSchema


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.updated_at))
        result = await session.execute(statement)

        return result.scalars().all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_user_book(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.execute(statement)

        return result.scalars().all()

    async def create_book(
        self, book_data: BookCreateSchema, user_uid: uuid.UUID, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid
        session.add(new_book)

        await session.commit()
        await session.refresh(new_book)

        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateSchema, session: AsyncSession
    ):
        update_book = await self.get_book(book_uid, session)
        if not update_book:
            return None

        update_book_dict = update_data.model_dump()
        for key, value in update_book_dict.items():
            if value is not None:
                setattr(update_book, key, value)

        await session.commit()
        await session.refresh(update_book)

        return update_book

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book = await self.get_book(book_uid, session)
        if not book:
            return False

        await session.delete(book)
        await session.commit()

        return True
