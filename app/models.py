from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Reminder:
    id: int
    user_id: int
    title: str
    reminder_date: date
    notified: bool
