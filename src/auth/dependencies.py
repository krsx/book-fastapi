from datetime import datetime
from typing import Any, List
from fastapi import Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from typing_extensions import Annotated, Doc
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.auth.utils import decode_token, create_access_token
from src.db.main import get_session
from src.db.redis import token_in_blocklist
from src.auth.services import AuthService
from src.errors import (
    AccessTokenRequired,
    AccountNotVerified,
    InvalidToken,
    InsufficientPermission,
    RefreshTokenRequired,
)


auth_service = AuthService()


class TokenBearer(HTTPBearer):
    def __init__(
        self,
        *,
        bearerFormat: str | None = None,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        if creds is None:
            raise InvalidToken()

        token = creds.credentials

        if not self.token_valid(token):
            raise InvalidToken()

        token_data = decode_token(token)

        if await token_in_blocklist(token_data["jti"]):  # type: ignore
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data  # type: ignore

    def token_valid(self, token: str) -> bool:
        if not token:
            return False
        token_data = decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]
    user = await auth_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()

        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
