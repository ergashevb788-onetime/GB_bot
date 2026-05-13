"""
config.py — Loads and validates environment variables.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str
    OWNER_CHAT_ID: int
    SPECIAL_USER_ID: int
    WEBHOOK_URL: str
    PORT: int
    DATABASE_URL: str   # Added: PostgreSQL connection string

    @classmethod
    def from_env(cls) -> "Settings":
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN is missing from environment variables.")

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL is missing from environment variables.")

        owner_id    = os.getenv("OWNER_CHAT_ID", "0")
        SPECIAL_USER_ID = int(os.getenv("SPECIAL_USER_ID", "0"))
        webhook_url = os.getenv("WEBHOOK_URL", "").rstrip("/")
        port        = int(os.getenv("PORT", "8080"))

        return cls(
            BOT_TOKEN=bot_token,
            OWNER_CHAT_ID=int(owner_id),
            WEBHOOK_URL=webhook_url,
            PORT=port,
            DATABASE_URL=database_url,
        )


settings = Settings.from_env()
