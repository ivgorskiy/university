from enum import Enum
from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


# todo почитать про Enum
# Множественное наследование
# Enum-объект будет записываться в базу. При наследовании от str (на первом месте)
# enum-объект преобразуется в строку. Без преобразования попытка записи
# enum-объекта в базу приведёт к ошибке "Type error". Преобразование работает
# только если str стоит на первом месте.
# После преобразования в базу запишутся значения атрибутов.
# Также, если не наследовать от str, то в тех местах кода, где нужно явное
# строковое представление вместо roles=[PortalRole.ROLE_PORTAL_USER]
# нужно будет писать roles=[PortalRole.ROLE_PORTAL_USER.value]
class PortalRole(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


class UserDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        hashed_password: str,
        roles: list[PortalRole],
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()

        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        # Запрос для обновления
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )

        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()

        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()

        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()

        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )

        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()

        if update_user_id_row is not None:
            return update_user_id_row[0]
