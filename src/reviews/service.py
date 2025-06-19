import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from datetime import datetime

from src.db.models import Review
from src.reviews.schemas import ReviewCreateSchema
from src.auth.services import AuthService
from src.books.services import BookService
from src.errors import BookNotFound, UserNotFound, ReviewNotFound


book_service = BookService()
user_service = AuthService()


class ReviewService:
    async def add_review_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateSchema,
        session: AsyncSession,
    ):
        book = await book_service.get_book(book_uid, session)
        user = await user_service.get_user_by_email(user_email, session)
        review_data_dict = review_data.model_dump()
        new_review = Review(**review_data_dict)

        if not book:
            raise BookNotFound()

        if not user:
            raise UserNotFound()

        new_review.user = user
        new_review.book = book
        session.add(new_review)

        await session.commit()
        await session.refresh(new_review)

        return new_review

    async def get_review(
        self,
        review_uid: str,
        session: AsyncSession,
    ):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.execute(statement)

        return result.scalars().all()

    async def delete_review(
        self,
        review_uid: str,
        user_email: str,
        session: AsyncSession,
    ):
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            return UserNotFound()

        review = await self.get_review(review_uid, session)
        if not review:
            return ReviewNotFound()

        await session.delete(review)
        await session.commit()

        return {"success": True}
