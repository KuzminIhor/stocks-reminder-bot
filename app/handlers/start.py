from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.reminders import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привіт! 👋\nЯ допоможу стежити за датами твоїх записів.",
        reply_markup=main_menu(),
    )
