import hmac
import logging
import base64
import json
from urllib.parse import unquote, parse_qs
from hashlib import sha256
from typing import List, Optional

from fastapi import APIRouter
from fastapi.param_functions import Depends

from api.db.dao.user_dao import UserDAO
from api.db.models.user import UserModel
from api.settings import settings
from api.web.api.user.schema import (
    BasicResponseDTO,
    UserCreateInputDTO,
    UserCreateOutputDTO,
    UserModelDTO,
    ValidateDataInputDTO,
    Error,
    ErrorMsg,
    SetBirthdayDTO, SetPhotoURLDTO
)
from datetime import datetime

router = APIRouter()


@router.put("", response_model=None)
@router.put("/", response_model=None)
async def create_user(
    new_user: UserCreateInputDTO,
    user_dao: UserDAO = Depends(),
) -> BasicResponseDTO | UserCreateOutputDTO:
    """
    Creates new user in database

    :param new_user: new user model item.
    :param user_dao: DAO for user model.
    """
    status = await user_dao.create_user(
        new_user.chat_id, new_user.first_name,
        new_user.last_name, new_user.username,
        new_user.photo_url
    )

    user: UserModel = await user_dao.get_user(chat_id=new_user.chat_id)
    if user and status:
        return UserCreateOutputDTO(
            result=status,
            **user.__dict__,
            share_link=get_share_link(user.id)
        )
    return BasicResponseDTO(result=status)


def get_share_link(user_id: int):
    payload = base64.b64encode(str.encode(str(user_id))).decode().rstrip("=")
    invite_link = f"https://t.me/{settings.bot_username}/{settings.web_app_name}?" \
                  f"startapp={payload}"
    return invite_link


@router.get("", response_model=None)
@router.get("/", response_model=None)
async def get_users(
    id: Optional[int] = None,
    chat_id: Optional[int] = None,
    username: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    user_dao: UserDAO = Depends(),
) -> List[UserModelDTO] | UserModelDTO | None:
    """
    Get all users
    """
    if id is not None or chat_id is not None or username is not None:
        user = await user_dao.get_user(id=id, chat_id=chat_id, username=username)
        if not user:
            return None
        return UserModelDTO(**user.__dict__, share_link=get_share_link(user.id))

    users = await user_dao.get_all_users(limit=limit, offset=offset)
    if not users:
        return []

    return [UserModelDTO(**item.__dict__) for item in users]


@router.post("/validate_init_data", response_model=None)
async def validate_init_data(
    body: ValidateDataInputDTO,
    user_dao: UserDAO = Depends(),
) -> BasicResponseDTO | UserCreateOutputDTO:
    """
    Validates Init Data from Web App
    """
    parsed_data: dict = parse_qs(unquote(body.init_data))
    for key, value in parsed_data.items():
        parsed_data[key] = value[0]

    print(parsed_data)
    hex_hash = parsed_data.pop("hash")

    if not hex_hash:
        return BasicResponseDTO(
            result=False,
            detailed=Error(msg=ErrorMsg.VALIDATE_ERROR)
        )

    is_valid = check_hash(parsed_data, hex_hash)

    telegram_user = json.loads(str(parsed_data.get("user")))
    user: UserModel = await user_dao.get_user(chat_id=telegram_user.get("id"))

    if is_valid and user is None:
        user_data = UserCreateInputDTO(
            chat_id=telegram_user.get("id"),
            first_name=telegram_user.get("first_name"),
            last_name=telegram_user.get("last_name"),
            username=telegram_user.get("username"),
            photo_url=telegram_user.get("photo_url")
        )

        created_user: UserCreateOutputDTO = await create_user(user_data, user_dao)
        return created_user

    if is_valid and user is not None:
        return UserCreateOutputDTO(
            result=is_valid,
            **user.__dict__,
            share_link=get_share_link(user.id)
        )

    return BasicResponseDTO(result=False, detailed=Error(msg=ErrorMsg.UNKNOWN))


def check_hash(parsed_data, hex_hash) -> bool:
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=settings.bot_token.encode(),
        digestmod=sha256,
    )

    is_valid = (
        hmac.new(
            secret_key.digest(),
            data_check_string.encode(), sha256
        ).hexdigest() == hex_hash
    )

    return is_valid


@router.post("/birthday", response_model=BasicResponseDTO)
async def set_birthday(
    body: SetBirthdayDTO,
    user_dao: UserDAO = Depends(),
) -> BasicResponseDTO:
    status = await user_dao.set_birthday(body.user_id, body.birthday)
    return BasicResponseDTO(result=status)


@router.post("/photo_url", response_model=BasicResponseDTO)
async def set_photo_url(
    body: SetPhotoURLDTO,
    user_dao: UserDAO = Depends(),
) -> BasicResponseDTO:
    status = await user_dao.update_photo(body.user_id, body.photo_url)
    return BasicResponseDTO(result=status)
