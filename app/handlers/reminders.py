from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from app.services.notification_service import check_due_reminders

from app.config import settings
from app.keyboards.reminders import main_menu, reminder_actions
from app.services.reminder_service import (
    create_reminder,
    list_reminders,
    get_reminder,
    update_reminder_date,
    remove_reminder,
)

router = Router()
timezone = ZoneInfo(settings.timezone)


class AddReminder(StatesGroup):
    title = State()
    date = State()


class EditReminder(StatesGroup):
    date = State()


def parse_date(value: str):
    try:
        parsed = datetime.strptime(value.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None
    if parsed < datetime.now(timezone).date():
        return None
    return parsed


@router.message(F.text == "➕ Додати запис")
async def add_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddReminder.title)
    await message.answer("Введи назву запису:")


@router.message(AddReminder.title)
async def add_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer("Назва не може бути порожньою. Спробуй ще раз:")
        return
    if len(title) > 200:
        await message.answer("Максимальна довжина назви — 200 символів. Спробуй ще раз:")
        return

    await state.update_data(title=title)
    await state.set_state(AddReminder.date)
    await message.answer("Введи дату у форматі ДД.ММ.РРРР, наприклад 15.11.2026:")


@router.message(AddReminder.date)
async def add_date(message: Message, state: FSMContext) -> None:
    reminder_date = parse_date(message.text or "")
    if reminder_date is None:
        await message.answer("Дата некоректна або вже минула. Введи дату як ДД.ММ.РРРР:")
        return

    data = await state.get_data()
    await create_reminder(message.from_user.id, data["title"], reminder_date)
    await state.clear()
    await message.answer(
        f"✅ Запис додано!\n📝 {data['title']}\n📅 {reminder_date:%d.%m.%Y}",
        reply_markup=main_menu(),
    )


@router.message(F.text == "📋 Мої записи")
async def show_reminders(message: Message) -> None:
    reminders = await list_reminders(message.from_user.id)
    if not reminders:
        await message.answer("Записів поки немає.", reply_markup=main_menu())
        return

    await message.answer(f"📋 Твої записи: {len(reminders)}", reply_markup=main_menu())
    for item in reminders:
        status = "✅ Сповіщено" if item["notified"] else "🔔 Очікує сповіщення"
        await message.answer(
            f"📝 {item['title']}\n📅 {datetime.fromisoformat(item['reminder_date']).strftime('%d.%m.%Y')}\n{status}",
            reply_markup=reminder_actions(item["id"]),
        )


@router.callback_query(F.data.startswith("edit:"))
async def edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    reminder_id = int(callback.data.split(":")[1])
    reminder = await get_reminder(callback.from_user.id, reminder_id)
    if not reminder:
        await callback.answer("Запис не знайдено.", show_alert=True)
        return

    await state.clear()
    await state.update_data(reminder_id=reminder_id)
    await state.set_state(EditReminder.date)
    await callback.message.answer(
        f"Нова дата для «{reminder['title']}» у форматі ДД.ММ.РРРР:"
    )
    await callback.answer()


@router.message(EditReminder.date)
async def edit_date(message: Message, state: FSMContext) -> None:
    new_date = parse_date(message.text or "")
    if new_date is None:
        await message.answer("Дата некоректна або вже минула. Введи дату як ДД.ММ.РРРР:")
        return

    data = await state.get_data()
    updated = await update_reminder_date(
        message.from_user.id, data["reminder_id"], new_date
    )
    await state.clear()

    if not updated:
        await message.answer("Запис не знайдено.")
        return

    await message.answer(
        f"✅ Дату змінено на {new_date:%d.%m.%Y}.\n"
        "Прапорець сповіщення скинуто, тому запис може сповістити знову.",
        reply_markup=main_menu(),
    )


@router.callback_query(F.data.startswith("delete:"))
async def delete_callback(callback: CallbackQuery) -> None:
    reminder_id = int(callback.data.split(":")[1])
    deleted = await remove_reminder(callback.from_user.id, reminder_id)
    if deleted:
        await callback.message.edit_text("🗑️ Запис видалено.")
        await callback.answer("Видалено")
    else:
        await callback.answer("Запис не знайдено.", show_alert=True)

# Перевірка нагадувань через команду /test_notify
@router.message(Command("test_notify"))
async def test_notify(message: Message, bot: Bot):
    await message.answer("🔔 Запускаю тестову перевірку нагадувань...")
    await check_due_reminders(bot)
    await message.answer("✅ Перевірку завершено. Якщо є записи на сьогодні, перевір повідомлення вище.")