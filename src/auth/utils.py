from src.config import Config
from typing import Optional
from datetime import timedelta, datetime
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
import jwt
import uuid
import logging


# bypass bcrypt error
logging.getLogger("passlib").setLevel(logging.ERROR)


ACCESS_TOKEN_EXPIRTY = 3600

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-confirmation"
)


def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)


def create_access_token(
    user_data: dict, expiry: Optional[timedelta] = None, refresh: bool = False
):
    payload = {
        "user": user_data,
        "exp": datetime.now()
        + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRTY)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> Optional[dict]:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWKError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None


def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str):
    try:
        data = serializer.loads(token)
        return data
    except Exception as e:
        logging.exception(e)
        return None
