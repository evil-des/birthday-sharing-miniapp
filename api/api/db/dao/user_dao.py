from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import Depends
from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.dependencies import get_db_session
from api.db.models.user import UserModel
from api.settings import settings


class UserDAO:
    """Class for accessing users table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_user(
        self,
        chat_id: int,
        first_name: str,
        last_name: str,
        username: str,
        photo_url: str
    ) -> bool:
        user = UserModel(
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            photo_url=photo_url
        )
        self.session.add(user)

        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def set_birthday(
        self,
        user_id: int,
        birthday: datetime
    ) -> bool:
        user = await self.get_user(user_id)
        user.birthday = birthday

        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def update_photo(
        self,
        user_id: int,
        photo_url: str
    ) -> bool:
        user = await self.get_user(user_id)
        user.photo_url = photo_url

        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def get_user(
        self,
        id: int = None,
        chat_id: int = None,
        username: str = None
    ) -> UserModel | None:
        if id is None and chat_id is None and username is None:
            return None

        query = select(UserModel)
        if chat_id:
            query = query.where(UserModel.chat_id == chat_id)
        if id:
            query = query.where(UserModel.id == id)
        if username:
            query = query.where(UserModel.username == username)

        res = await self.session.execute(query)
        return res.scalars().first()

    async def get_all_users(self, limit: int = None, offset: int = None) -> List[
        UserModel]:
        """
        Get all users with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: list of users.
        """
        q = select(UserModel).order_by(UserModel.id)

        if limit and offset:
            q = select(UserModel).limit(limit).offset(offset)

        raw_users = await self.session.execute(q)
        return list(raw_users.scalars().fetchall())

    async def filtered_users(
        self,
        name: Optional[str] = None
    ) -> List[UserModel]:
        """
        :param name: tg name of user.
        :return: user models.
        """
        query = select(UserModel)

        if name:
            key_word = name.lower()
            query = (
                query
                .where(
                    or_(
                        UserModel.first_name.ilike("%" + key_word + "%+"),
                        UserModel.last_name.ilike("%" + key_word + "%+"),
                    )
                )
            )

        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
