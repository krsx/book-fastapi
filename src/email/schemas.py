from pydantic import BaseModel
from typing import List


class EmailSchema(BaseModel):
    addresses: List[str]


class PasswordResetRequestSchema(BaseModel):
    email: str


class PasswordResetConfirmationSchema(BaseModel):
    new_password: str
    confirm_password: str
