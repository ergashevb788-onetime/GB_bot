"""
keyboards.py — All ReplyKeyboard and InlineKeyboard definitions.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# ─── Main Menu ────────────────────────────────────────────────────────────────

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Reading Space")],
            [KeyboardButton(text="🌱 Habit Tracker")],
            [KeyboardButton(text="💌 Little Things")],
        ],
        resize_keyboard=True,
        input_field_placeholder="What would you like to do today?",
    )


# ─── Reading Space ────────────────────────────────────────────────────────────
def finish_book_inline(book_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes, I finished it!", callback_data=f"finish_book:{book_id}"),
                InlineKeyboardButton(text="📖 Still reading",      callback_data="still_reading"),
            ]
        ]
    )
    
def reading_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Update Progress"), KeyboardButton(text="💭 Save Quote")],
            [KeyboardButton(text="📚 My Library"),      KeyboardButton(text="✨ Random Quote")],
            [KeyboardButton(text="✅ Finish Book"),      KeyboardButton(text="⏰ Reading Reminder")],
            [KeyboardButton(text="⬅ Back")],
        ],
        resize_keyboard=True,
    )


# ─── Habit Tracker ────────────────────────────────────────────────────────────

def habits_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Today's Habits")],
            [KeyboardButton(text="📈 Weekly Progress"), KeyboardButton(text="⏰ Habit Reminder")],
            [KeyboardButton(text="🌙 Daily Reflection")],
            [KeyboardButton(text="⬅ Back")],
        ],
        resize_keyboard=True,
    )


def today_habits_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Add Habit"), KeyboardButton(text="➖ Remove Habit")],
            [KeyboardButton(text="⬅ Back")],
        ],
        resize_keyboard=True,
    )


# ─── Habits toggle (inline) ───────────────────────────────────────────────────

def habits_inline(habits: list[dict], completions: dict[int, bool]) -> InlineKeyboardMarkup:
    """Build inline keyboard with toggle buttons for each habit."""
    buttons = []
    for habit in habits:
        hid = habit["id"]
        done = completions.get(hid, False)
        icon = "✅" if done else "⬜"
        buttons.append(
            [InlineKeyboardButton(
                text=f"{icon} {habit['name']}",
                callback_data=f"toggle_habit:{hid}",
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def remove_habit_inline(habits: list[dict]) -> InlineKeyboardMarkup:
    """Build inline keyboard to select a habit for removal."""
    buttons = [
        [InlineKeyboardButton(
            text=f"🗑 {habit['name']}",
            callback_data=f"remove_habit:{habit['id']}",
        )]
        for habit in habits
    ]
    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="cancel_remove")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── Little Things ────────────────────────────────────────────────────────────

def little_things_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="😂 Joke"),          KeyboardButton(text="🤍 I Miss You")],
            [KeyboardButton(text="🫂 Hug"),            KeyboardButton(text="✨ Random Comfort")],
            [KeyboardButton(text="⬅ Back")],
        ],
        resize_keyboard=True,
    )


# ─── Daily Reflection ─────────────────────────────────────────────────────────

def reflection_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😊 Good",    callback_data="mood:good"),
                InlineKeyboardButton(text="😌 Calm",    callback_data="mood:calm"),
            ],
            [
                InlineKeyboardButton(text="😔 Tiring",  callback_data="mood:tiring"),
                InlineKeyboardButton(text="😵 Busy",    callback_data="mood:busy"),
            ],
        ]
    )


# ─── Reading Reminder Toggle ──────────────────────────────────────────────────

def reading_reminder_inline(enabled: bool) -> InlineKeyboardMarkup:
    label = "🔕 Disable Reminder" if enabled else "🔔 Enable Reminder"
    action = "reminder:reading:off" if enabled else "reminder:reading:on"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=action)]]
    )


def habit_reminder_inline(enabled: bool) -> InlineKeyboardMarkup:
    label = "🔕 Disable Reminder" if enabled else "🔔 Enable Reminder"
    action = "reminder:habit:off" if enabled else "reminder:habit:on"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=action)]]
    )


# ─── Add book prompt (inline) ─────────────────────────────────────────────────

def add_book_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add a book", callback_data="add_book")],
        ]
    )
