from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.db.main import get_session
from src.auth.dependencies import (
    RoleChecker,
    TokenBearer,
    AccessTokenBearer,
    RefreshTokenBearer,
    get_current_user,
)
from src.reviews.schemas import ReviewCreateSchema, ReviewSchema
from src.reviews.service import ReviewService
from src.errors import ReviewNotFound


review_router = APIRouter()
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()
admin_user_role = RoleChecker(["admin", "user"])


@review_router.post(
    "/{book_uid}",
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_user_role)],
)
async def add_review(
    book_uid: str,
    review_data: ReviewCreateSchema,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_book(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )

    return new_review


@review_router.get(
    "/", response_model=List[ReviewSchema], dependencies=[Depends(admin_user_role)]
)
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_service.get_all_reviews(session)
    return reviews


@review_router.get(
    "/{review_uid}",
    response_model=ReviewSchema,
    dependencies=[Depends(admin_user_role)],
)
async def get_review(
    review_uid: str,
    session: AsyncSession = Depends(get_session),
):
    review = await review_service.get_review(review_uid, session)
    if not review:
        raise ReviewNotFound()

    return review


@review_router.delete(
    "/{review_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_user_role)],
)
async def delete_review(
    review_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    await review_service.delete_review(review_uid, current_user.email, session)

    return {}
