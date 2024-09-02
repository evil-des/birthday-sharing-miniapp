from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from app.utils.get_settings import get_settings

router = Router()
settings = get_settings()


@router.message(CommandStart())
async def start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Перейти", web_app=WebAppInfo(url=settings.WEB_APP_URL))
        ]]
    )
    await message.answer(
        "Нажмите на кнопку, чтобы начать работу с Telegram Mini App!",
        reply_markup=kb
    )
