from src.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from src.auth.schemas import UserCreateSchema, UserUpdateSchema
from src.auth.utils import generate_password_hash


class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return user is not None

    async def create_user(self, user_data: UserCreateSchema, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    async def update_user(self, user: User, update_data: dict, session: AsyncSession):
        user_data = await self.get_user_by_email(user.email, session)
        if not user_data:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(user_data, key, value)

        await session.commit()
        await session.refresh(user_data)

        return user_data
