import enum
from typing import Any, Optional, List
from datetime import datetime

from pydantic import BaseModel


class ErrorMsg(enum.Enum):
    UNKNOWN = "Произошла неизвестная ошибка. Попробуйте позже"
    VALIDATE_ERROR = "Произошла ошибка при авторизации. " \
                     "Попробуйте перезайти в приложение"
    USER_BANNED = "Ваш аккаунт заблокирован"
    NOT_REGISTERED = "Вы не прошли регистрацию. " \
                     "Обратитесь к администратору, если вы видете эту ошибку"
    TWINK_DETECTED = "Обнаружена попытка нарушить правила пользования сервисом. " \
                     "Повторите вход в приложение позже."


class Error(BaseModel):
    msg: ErrorMsg = ErrorMsg.UNKNOWN


class Item(BaseModel):
    pass


class BasicResponseDTO(BaseModel):
    result: bool
    detailed: Optional[Error | Item | List[Item]] = None


class UserCreateInputDTO(BaseModel):
    """
    DTO for user model.

    It returned when accessing dummy models from the API.
    """

    chat_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    birthday: Optional[datetime] = None


class UserModelDTO(UserCreateInputDTO):
    id: int
    share_link: Optional[str] = None
    date_started: datetime


class UserCreateOutputDTO(BasicResponseDTO, UserModelDTO):
    pass


class ValidateDataInputDTO(BaseModel):
    init_data: str


class SetBirthdayDTO(BaseModel):
    user_id: int
    birthday: datetime


class SetPhotoURLDTO(BaseModel):
    user_id: int
    photo_url: str
