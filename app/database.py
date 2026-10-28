import aiosqlite

DB_PATH = "reminders.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                reminder_date TEXT NOT NULL,
                notified INTEGER NOT NULL DEFAULT 0
                    CHECK (notified IN (0, 1))
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_reminders_date_notified
            ON reminders (reminder_date, notified)
        """)
        await db.commit()


async def fetch_all(query: str, params: tuple = ()) -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def execute(query: str, params: tuple = ()) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, params)
        await db.commit()
