from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Додати запис"),
                KeyboardButton(text="📋 Мої записи"),
            ]
        ],
        resize_keyboard=True,
    )


def reminder_actions(reminder_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Змінити дату",
                    callback_data=f"edit:{reminder_id}",
                ),
                InlineKeyboardButton(
                    text="🗑️ Видалити",
                    callback_data=f"delete:{reminder_id}",
                ),
            ]
        ]
    )
