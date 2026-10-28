import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import init_db
from app.handlers.start import router as start_router
from app.handlers.reminders import router as reminders_router
from app.services.notification_service import check_due_reminders

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(reminders_router)

    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    scheduler.add_job(
        check_due_reminders,
        trigger="cron",
        hour=9,
        minute=0,
        args=[bot],
        id="daily_reminders",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
    scheduler.start()

    try:
        logging.info("Bot started; daily check scheduled for 09:00 (%s).", settings.timezone)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
