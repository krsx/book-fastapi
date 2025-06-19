from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BookException(Exception):
    """This is the base class for all book errors"""

    pass


class InvalidToken(BookException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(BookException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(BookException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(BookException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(BookException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(BookException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(BookException):
    """User does not have the necessary permissions to perform an action."""

    pass


class BookNotFound(BookException):
    """Book Not found"""

    pass


class UserNotFound(BookException):
    """User Not found"""

    pass


class ReviewNotFound(BookException):
    """Review Not found"""

    pass


class VerificationFailed(BookException):
    """Verification of user failed"""

    pass


class AccountNotVerified(BookException):
    """User account is not verified"""

    pass


class NewPasswordNotMatch(BookException):
    """New password does not match the confirmation password"""

    pass


class PasswordResetFailed(BookException):
    """Password reset failed due to an unknown error"""

    pass


def create_exception_handler(
    status_code: int, handler_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BookException):
        return JSONResponse(content=handler_detail, status_code=status_code)

    return exception_handler  # type: ignore


def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            handler_detail={
                "detail": "Invalid token provided. Please provide a valid token.",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            handler_detail={
                "detail": "The provided token has been revoked. Please log in again.",
                "error_code": "revoked_token",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            handler_detail={
                "detail": "Access token is required for this operation.",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            handler_detail={
                "detail": "Refresh token is required for this operation.",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            handler_detail={
                "detail": "User with this email already exists.",
                "error_code": "user_already_exists",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            handler_detail={
                "detail": "Invalid email or password provided.",
                "error_code": "invalid_credentials",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            handler_detail={
                "detail": "You do not have sufficient permissions to perform this action.",
                "error_code": "insufficient_permission",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            handler_detail={
                "detail": "The requested book was not found.",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            handler_detail={
                "detail": "The requested user was not found.",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        ReviewNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            handler_detail={
                "detail": "The requested review was not found.",
                "error_code": "review_not_found",
            },
        ),
    )

    app.add_exception_handler(
        VerificationFailed,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            handler_detail={
                "detail": "User verification failed. Please try again.",
                "error_code": "verification_failed",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            handler_detail={
                "detail": "User account is not verified. Please verify your account via registered email.",
                "error_code": "account_not_verified",
            },
        ),
    )

    app.add_exception_handler(
        NewPasswordNotMatch,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            handler_detail={
                "detail": "New password does not match the confirmation password.",
                "error_code": "new_password_not_match",
            },
        ),
    )

    app.add_exception_handler(
        PasswordResetFailed,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            handler_detail={
                "detail": "Password reset failed due to an unknown error.",
                "error_code": "password_reset_failed",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred. Please try again later.",
                "error_code": "internal_server_error",
            },
        )
