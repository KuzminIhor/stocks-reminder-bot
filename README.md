# Telegram Reminder Bot

## Setup (Windows / PowerShell)

1. Create and activate the virtual environment:
   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and put your BotFather token in `BOT_TOKEN`.
4. Run from the project root:
   ```powershell
   python -m app.main
   ```

The bot checks reminders every day at 09:00 in `Europe/Bratislava`.
Each reminder has a `notified` boolean-like SQLite field (`0` / `1`).
Changing the date resets `notified` to `0`.
