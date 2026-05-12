"""
handlers/start.py — /start command and main menu.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import database as db
from keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    name = user.first_name or "friend"

    # Register user (creates default habits on first visit)
    await db.get_or_create_user(
        user_id=user.id,
        username=user.username or "",
        first_name=name,
    )

    await message.answer(
        f"✨ Welcome back, {name}.\n\n"
        "A small space for your books, habits, and quiet moments 📖\n\n"
        "What would you like to do today?",
        reply_markup=main_menu(),
    )
