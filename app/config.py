import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    timezone: str = "Europe/Bratislava"


_token = os.getenv("BOT_TOKEN")
if not _token:
    raise RuntimeError("BOT_TOKEN is missing. Add it to the .env file.")

settings = Settings(
    bot_token=_token,
    timezone=os.getenv("TIMEZONE", "Europe/Bratislava"),
)
