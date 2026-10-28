import logging
from datetime import date, datetime
from zoneinfo import ZoneInfo

import aiosqlite
from aiogram import Bot

from app.config import settings
from app.database import DB_PATH

logger = logging.getLogger(__name__)
timezone = ZoneInfo(settings.timezone)


async def check_due_reminders(bot: Bot) -> None:
    today = datetime.now(timezone).date().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, user_id, title, reminder_date
            FROM reminders
            WHERE reminder_date = ? AND notified = 0
            """,
            (today,),
        )
        reminders = await cursor.fetchall()

    for reminder in reminders:
        try:
            await bot.send_message(
                reminder["user_id"],
                "🔔 Перевірте запис:\n\n"
                f"📝 {reminder['title']}\n"
                f"📅 {date.fromisoformat(reminder['reminder_date']):%d.%m.%Y}",
            )
        except Exception:
            logger.exception("Could not send reminder id=%s", reminder["id"])
            continue

        # Позначаємо сповіщеним лише після успішного надсилання.
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE reminders SET notified = 1 WHERE id = ? AND notified = 0",
                (reminder["id"],),
            )
            await db.commit()
