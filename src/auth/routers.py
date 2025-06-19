from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,  # type: ignore
    RoleChecker,
)
from src.auth.schemas import (
    UserCreateSchema,
    UserDetailsSchema,
    UserLoginSchema,
    UserSchema,
)
from src.auth.services import AuthService
from src.auth.utils import (
    create_access_token,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
    generate_password_hash,
)
from src.db.main import get_session
from src.db.models import User
from src.db.redis import add_jti_to_blocklist
from src.email.schemas import (
    EmailSchema,
    PasswordResetConfirmationSchema,
    PasswordResetRequestSchema,
)
from src.errors import (
    InvalidToken,
    NewPasswordNotMatch,
    PasswordResetFailed,
    UserAlreadyExists,
    InvalidCredentials,
    UserNotFound,
    VerificationFailed,
)
from src.email.mail import mail, create_message
from src.celery_task import send_email_task
from src.config import Config


REFRESH_TOKEN_EXPIRTY = 2


auth_router = APIRouter()
auth_service = AuthService()
admin_user_role = RoleChecker(["admin", "user"])


@auth_router.post(
    "/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    user_exist = await auth_service.user_exists(email, session)

    if user_exist:
        raise UserAlreadyExists()

    new_user = await auth_service.create_user(user_data, session)
    token = create_url_safe_token(
        {
            "email": email,
        }
    )
    verification_link = (
        f"http://{Config.DOMAIN}/api/{Config.API_VERSION}/auth/verify_email/{token}"
    )
    html_message = """
    <h1>Verify Your Email</h1>
    <p>Thank you for signing up! Please click the link below to verify your email address:</p>
    <a href="{verification_link}">Verify Email</a>
    """
    # message = create_message(
    #     recipients=[email],
    #     subject="Email Verification",
    #     body=html_message.format(verification_link=verification_link),
    # )
    # await mail.send_message(message)

    send_email_task.delay(  # type: ignore
        [email],
        "Email Verification",
        html_message.format(verification_link=verification_link),
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User created successfully. Please check your email to verify your account.",
            "user": {
                "email": new_user.email,
                "uid": str(new_user.uid),
                "role": new_user.role,
                "verified": new_user.is_verified,
            },
        },
    )


@auth_router.get("/verify_email/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if token_data is None or "email" not in token_data:
        raise InvalidToken()

    user_email = token_data["email"]
    if user_email:
        user = await auth_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await auth_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Email verified successfully. You can now log in.",
                "user": {
                    "email": user.email,
                    "uid": str(user.uid),
                    "role": user.role,
                    "verified": user.is_verified,
                },
            },
        )

    return VerificationFailed()


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginSchema, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await auth_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRTY),
            )

            response = JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                        "role": user.role,
                        "verified": user.is_verified,
                    },
                },
            )

            return response

    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expired_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expired_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get("/status", response_model=UserDetailsSchema)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(admin_user_role)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Logged out successfully"},
    )


@auth_router.post("/send_email")
async def send_email(emails: EmailSchema):
    addresses = emails.addresses

    html = "<h1>Test Email</h1><p>This is a test email.</p>"
    subject = "Test Email"

    # message = create_message(
    #     recipients=addresses,
    #     subject=subject,
    #     body=html,
    # )

    # await mail.send_message(message)
    send_email_task.delay(  # type: ignore
        addresses,
        subject,
        html,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email sent successfully"},
    )


@auth_router.post("/password_reset")
async def password_reset(
    email_data: PasswordResetRequestSchema,
):
    email = email_data.email
    token = create_url_safe_token({"email": email})
    verification_link = f"http://{Config.DOMAIN}/api/{Config.API_VERSION}/auth/password_reset_confirm/{token}"
    html_message = """
    <h1>Password Reset Request</h1>
    <p>We received a request to reset your password. Please click the link below to reset your password:</p>
    <a href="{verification_link}">Reset Password</a>
    """
    # message = create_message(
    #     recipients=[email],
    #     subject="Reset Your Password",
    #     body=html_message.format(verification_link=verification_link),
    # )

    # await mail.send_message(message)

    send_email_task.delay(  # type: ignore
        [email],
        "Reset Your Password",
        html_message.format(verification_link=verification_link),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Password reset email sent successfully. Please check your email.",
            "verification_link": verification_link,
        },
    )


@auth_router.post("/password_reset_confirm/{token}")
async def password_reset_confirm(
    token: str,
    passwords: PasswordResetConfirmationSchema,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_password
    if new_password != confirm_password:
        raise NewPasswordNotMatch()

    token_data = decode_url_safe_token(token)
    if token_data is None or "email" not in token_data:
        raise InvalidToken()

    user_email = token_data["email"]
    if user_email:
        user = await auth_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        password_hash = generate_password_hash(new_password)
        await auth_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Password reset successfully. You can now log in with your new password.",
                "user": {
                    "email": user.email,
                    "uid": str(user.uid),
                    "role": user.role,
                    "verified": user.is_verified,
                },
            },
        )

    return PasswordResetFailed()
