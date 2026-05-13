"""
config.py — Loads and validates environment variables.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str
    OWNER_CHAT_ID: int
    WEBHOOK_URL: str
    PORT: int
    DATABASE_URL: str
    SPECIAL_USER_ID: int = 0   # defaults to 0 if not set — never crashes

    @classmethod
    def from_env(cls) -> "Settings":
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN is missing from environment variables.")

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL is missing from environment variables.")

        return cls(
            BOT_TOKEN=bot_token,
            OWNER_CHAT_ID=int(os.getenv("OWNER_CHAT_ID", "0")),
            WEBHOOK_URL=os.getenv("WEBHOOK_URL", "").rstrip("/"),
            PORT=int(os.getenv("PORT", "8080")),
            DATABASE_URL=database_url,
            SPECIAL_USER_ID=int(os.getenv("SPECIAL_USER_ID", "0")),
        )


settings = Settings.from_env()
