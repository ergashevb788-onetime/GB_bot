"""
handlers/little_things.py — Little Things: jokes, I Miss You, hug, comfort.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from aiogram import Bot

import database as db
from keyboards import little_things_menu, main_menu
from utils.jokes import get_random_joke
from utils.messages import random_hug, random_comfort
from config import settings
from database import log_little_thing

router = Router()


# ─── Little Things Entry ──────────────────────────────────────────────────────

@router.message(F.text == "💌 Little Things")
async def little_things(message: Message, state: FSMContext) -> None:
    allowed = {settings.OWNER_CHAT_ID, settings.SPECIAL_USER_ID}
    if message.from_user.id not in allowed:
        await message.answer("This button is only for a certain person 🤍")
        return

    await state.clear()
    await message.answer(
        "💌 A quiet corner for small joys\n\nWhat do you need right now?",
        reply_markup=little_things_menu(),
    )


# ─── Joke ─────────────────────────────────────────────────────────────────────

@router.message(F.text == "😂 Joke")
async def send_joke(message: Message) -> None:
    await log_little_thing(message.from_user.id, "joke")
    await message.answer(get_random_joke())

# ─── I Miss You ───────────────────────────────────────────────────────────────

@router.message(F.text == "🤍 I Miss You")
async def i_miss_you(message: Message, bot: Bot) -> None:
    await log_little_thing(message.from_user.id, "i_miss_you")
    user = message.from_user
    name = user.first_name or user.username or "Someone"

    if settings.OWNER_CHAT_ID and settings.OWNER_CHAT_ID != 0:
        try:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            username = f"@{user.username}" if user.username else "no username"

            await bot.send_message(
                settings.OWNER_CHAT_ID,
                f"🤍 I Miss You\n\n"
                f"👤 {name} ({username})\n"
                f"🕐 {now}",
            )
        except Exception:
            pass

    await message.answer("Message delivered ✨")


# ─── Hug ──────────────────────────────────────────────────────────────────────

@router.message(F.text == "🫂 Hug")
async def send_hug(message: Message) -> None:
    await log_little_thing(message.from_user.id, "hug")
    await message.answer(random_hug())



# ─── Random Comfort ───────────────────────────────────────────────────────────

@router.message(F.text == "✨ Random Comfort")
async def send_comfort(message: Message) -> None:
    await log_little_thing(message.from_user.id, "comfort")
    await message.answer(random_comfort())

# ─── Back ─────────────────────────────────────────────────────────────────────

@router.message(F.text == "⬅ Back")
async def go_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Back to the main space 🌱", reply_markup=main_menu())
