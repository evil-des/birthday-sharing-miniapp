import enum
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Integer, String, Float

from api.db.base import Base
from api.settings import settings


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger(), unique=True)

    first_name: Mapped[str] = mapped_column(String(length=50), nullable=True,
                                            default="")  # noqa: WPS432
    last_name: Mapped[str] = mapped_column(String(length=50), nullable=True,
                                           default="")  # noqa: WPS432
    username: Mapped[str] = mapped_column(String(length=50), nullable=True,
                                          default="")  # noqa: WPS432
    birthday: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None)
    photo_url: Mapped[str] = mapped_column(String(length=50),
                                           nullable=True, default=None)

    date_started: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now(),)
