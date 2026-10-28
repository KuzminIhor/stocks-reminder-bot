from datetime import date

from app.database import execute, fetch_all


async def create_reminder(user_id: int, title: str, reminder_date: date) -> None:
    await execute(
        """
        INSERT INTO reminders (user_id, title, reminder_date, notified)
        VALUES (?, ?, ?, 0)
        """,
        (user_id, title, reminder_date.isoformat()),
    )


async def list_reminders(user_id: int):
    return await fetch_all(
        """
        SELECT id, user_id, title, reminder_date, notified
        FROM reminders
        WHERE user_id = ?
        ORDER BY reminder_date, id
        """,
        (user_id,),
    )


async def get_reminder(user_id: int, reminder_id: int):
    rows = await fetch_all(
        """
        SELECT id, user_id, title, reminder_date, notified
        FROM reminders
        WHERE id = ? AND user_id = ?
        LIMIT 1
        """,
        (reminder_id, user_id),
    )
    return rows[0] if rows else None


async def update_reminder_date(
    user_id: int, reminder_id: int, new_date: date
) -> bool:
    # Зміна дати скидає notified у 0.
    from app.database import DB_PATH
    import aiosqlite

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            UPDATE reminders
            SET reminder_date = ?, notified = 0
            WHERE id = ? AND user_id = ?
            """,
            (new_date.isoformat(), reminder_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def remove_reminder(user_id: int, reminder_id: int) -> bool:
    from app.database import DB_PATH
    import aiosqlite

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM reminders WHERE id = ? AND user_id = ?",
            (reminder_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0
