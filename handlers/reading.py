"""
handlers/reading.py — Reading Space: progress, quotes, library, reminders.
Uses FSM for multi-step flows.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import (
    reading_menu,
    main_menu,
    reading_reminder_inline,
    add_book_inline,
)
from utils.quotes import get_random_quote
from utils.messages import reading_progress_response

router = Router()


# ─── FSM States ───────────────────────────────────────────────────────────────

class ReadingStates(StatesGroup):
    waiting_for_page      = State()
    waiting_for_new_book  = State()
    waiting_for_quote     = State()
    waiting_for_quote_book = State()


# ─── Reading Space Entry ──────────────────────────────────────────────────────

@router.message(F.text == "📚 Reading Space")
async def reading_space(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    book = await db.get_current_book(user_id)
    pages_today = await db.get_pages_read_today(user_id)

    if book:
        text = (
            "📖 <b>Reading Space</b>\n\n"
            f"Currently reading:\n<i>{book['title']}</i> — Page {book['current_page']}\n\n"
            f"Today's reading:\n{pages_today} pages ✨\n\n"
            "What would you like to do?"
        )
    else:
        text = (
            "📖 <b>Reading Space</b>\n\n"
            "You haven't added a book yet 🌱\n\n"
            "What would you like to do?"
        )

    await message.answer(text, reply_markup=reading_menu(), parse_mode="HTML")


# ─── Update Progress ─────────────────────────────────────────────────────────

@router.message(F.text == "➕ Update Progress")
async def update_progress_start(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    book = await db.get_current_book(user_id)

    if not book:
        await message.answer(
            "You're not reading anything right now 📖\n\n"
            "What's the title of your current book?",
            reply_markup=add_book_inline(),
        )
        await state.set_state(ReadingStates.waiting_for_new_book)
        return

    await state.update_data(book_id=book["id"])
    await message.answer(
        f"You're on page <b>{book['current_page']}</b> of <i>{book['title']}</i>\n\n"
        "What page are you on now?",
        parse_mode="HTML",
    )
    await state.set_state(ReadingStates.waiting_for_page)


@router.callback_query(F.data == "add_book")
async def add_book_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("What's the title of the book you're reading? 📖")
    await state.set_state(ReadingStates.waiting_for_new_book)
    await callback.answer()


@router.message(ReadingStates.waiting_for_new_book)
async def receive_book_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    user_id = message.from_user.id
    book_id = await db.add_book(user_id, title)

    await state.update_data(book_id=book_id)
    await message.answer(
        f"Added <i>{title}</i> to your library 📚\n\n"
        "What page are you starting from?",
        parse_mode="HTML",
    )
    await state.set_state(ReadingStates.waiting_for_page)


@router.message(ReadingStates.waiting_for_page)
async def receive_page(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("Just the page number is fine 🌱 (e.g. 42)")
        return

    new_page = int(text)
    user_id = message.from_user.id
    data = await state.get_data()
    book_id = data.get("book_id")

    pages_read = await db.update_book_page(user_id, book_id, new_page)
    response = reading_progress_response(pages_read)

    await message.answer(response, reply_markup=reading_menu())
    await state.clear()


# ─── Save Quote ───────────────────────────────────────────────────────────────

@router.message(F.text == "💭 Save Quote")
async def save_quote_start(message: Message, state: FSMContext) -> None:
    await message.answer("Share the quote you'd like to keep 💭")
    await state.set_state(ReadingStates.waiting_for_quote)


@router.message(ReadingStates.waiting_for_quote)
async def receive_quote_text(message: Message, state: FSMContext) -> None:
    await state.update_data(quote_text=message.text.strip())
    await message.answer(
        "Which book is it from? (or just press /skip to save without a book name)"
    )
    await state.set_state(ReadingStates.waiting_for_quote_book)


@router.message(ReadingStates.waiting_for_quote_book)
async def receive_quote_book(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    quote_text = data["quote_text"]
    book_name = None if message.text.strip().lower() in ("/skip", "skip") else message.text.strip()

    await db.save_quote(message.from_user.id, quote_text, book_name)
    await message.answer("Saved to your reading corner ✨", reply_markup=reading_menu())
    await state.clear()


# ─── My Library ───────────────────────────────────────────────────────────────

@router.message(F.text == "📚 My Library")
async def my_library(message: Message, state: FSMContext) -> None:
    await state.clear()
    books = await db.get_all_books(message.from_user.id)

    if not books:
        await message.answer(
            "Your library is empty for now 📚\n\nAdd your first book via ➕ Update Progress.",
            reply_markup=reading_menu(),
        )
        return

    reading = [b for b in books if b["status"] == "reading"]
    finished = [b for b in books if b["status"] == "finished"]

    lines = ["📚 <b>My Library</b>\n"]

    if reading:
        lines.append("<b>Currently Reading</b>")
        for b in reading:
            lines.append(f"  📖 <i>{b['title']}</i> — p. {b['current_page']}")

    if finished:
        lines.append("\n<b>Finished</b>")
        for b in finished:
            lines.append(f"  ✅ <i>{b['title']}</i>")

    await message.answer("\n".join(lines), reply_markup=reading_menu(), parse_mode="HTML")


# ─── Random Quote ────────────────────────────────────────────────────────────

@router.message(F.text == "✨ Random Quote")
async def random_quote(message: Message) -> None:
    await message.answer(get_random_quote())


# ─── Reading Reminder ────────────────────────────────────────────────────────

@router.message(F.text == "⏰ Reading Reminder")
async def reading_reminder_settings(message: Message) -> None:
    user_settings = await db.get_user_settings(message.from_user.id)
    enabled = bool(user_settings.get("reading_reminder", 1))

    status = "on 🔔" if enabled else "off 🔕"
    await message.answer(
        f"Reading reminder is currently <b>{status}</b>\n\n"
        "If you haven't read in 2 days, I'll send a gentle nudge 🌱",
        reply_markup=reading_reminder_inline(enabled),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("reminder:reading:"))
async def toggle_reading_reminder(callback: CallbackQuery) -> None:
    action = callback.data.split(":")[-1]  # "on" or "off"
    new_value = 1 if action == "on" else 0
    await db.update_user_setting(callback.from_user.id, "reading_reminder", new_value)

    status = "enabled 🔔" if new_value else "disabled 🔕"
    await callback.message.edit_text(
        f"Reading reminder {status} ✨",
        reply_markup=reading_reminder_inline(bool(new_value)),
    )
    await callback.answer()


# ─── Back ─────────────────────────────────────────────────────────────────────

@router.message(F.text == "⬅ Back")
async def go_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Back to the main space 🌱", reply_markup=main_menu())
