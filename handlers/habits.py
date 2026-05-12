"""
handlers/habits.py — Habit Tracker: today's habits, weekly stats, reflection, reminders.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import (
    habits_menu,
    today_habits_menu,
    main_menu,
    habits_inline,
    remove_habit_inline,
    reflection_inline,
    habit_reminder_inline,
)
from utils.messages import mood_responses

router = Router()


# ─── FSM States ───────────────────────────────────────────────────────────────

class HabitStates(StatesGroup):
    waiting_for_habit_name = State()


# ─── Habit Tracker Entry ──────────────────────────────────────────────────────

@router.message(F.text == "🌱 Habit Tracker")
async def habit_tracker(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🌱 <b>Habit Tracker</b>\n\nWhat would you like to do?",
        reply_markup=habits_menu(),
        parse_mode="HTML",
    )


# ─── Today's Habits ──────────────────────────────────────────────────────────

@router.message(F.text == "✅ Today's Habits")
async def todays_habits(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    habits = await db.get_user_habits(user_id)
    completions = await db.get_habit_completions_today(user_id)

    if not habits:
        await message.answer(
            "No habits yet 🌱 Add your first one below.",
            reply_markup=today_habits_menu(),
        )
        return

    done_count = sum(1 for h in habits if completions.get(h["id"], False))
    total = len(habits)

    await message.answer(
        f"✅ <b>Today's Habits</b>\n\n"
        f"{done_count}/{total} complete — tap to toggle 🌱",
        reply_markup=habits_inline(habits, completions),
        parse_mode="HTML",
    )
    await message.answer("Manage your habits:", reply_markup=today_habits_menu())


@router.callback_query(F.data.startswith("toggle_habit:"))
async def toggle_habit_callback(callback: CallbackQuery) -> None:
    habit_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    new_state = await db.toggle_habit(user_id, habit_id)

    # Refresh the inline keyboard
    habits = await db.get_user_habits(user_id)
    completions = await db.get_habit_completions_today(user_id)
    done_count = sum(1 for h in habits if completions.get(h["id"], False))
    total = len(habits)

    response = "✅ Done ✨" if new_state else "Unmarked 🌱"
    await callback.answer(response)

    await callback.message.edit_text(
        f"✅ <b>Today's Habits</b>\n\n"
        f"{done_count}/{total} complete — tap to toggle 🌱",
        reply_markup=habits_inline(habits, completions),
        parse_mode="HTML",
    )


# ─── Add Habit ────────────────────────────────────────────────────────────────

@router.message(F.text == "➕ Add Habit")
async def add_habit_start(message: Message, state: FSMContext) -> None:
    await message.answer(
        "What habit would you like to add? 🌱\n\n"
        "(You can include an emoji, e.g. 🏃 Running)"
    )
    await state.set_state(HabitStates.waiting_for_habit_name)


@router.message(HabitStates.waiting_for_habit_name)
async def receive_habit_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    await db.add_habit(message.from_user.id, name)
    await message.answer(
        f"Added <b>{name}</b> to your habits ✨",
        reply_markup=today_habits_menu(),
        parse_mode="HTML",
    )
    await state.clear()


# ─── Remove Habit ────────────────────────────────────────────────────────────

@router.message(F.text == "➖ Remove Habit")
async def remove_habit_start(message: Message) -> None:
    user_id = message.from_user.id
    habits = await db.get_user_habits(user_id)

    if not habits:
        await message.answer("Nothing to remove yet 🌱", reply_markup=today_habits_menu())
        return

    await message.answer(
        "Which habit would you like to remove?",
        reply_markup=remove_habit_inline(habits),
    )


@router.callback_query(F.data.startswith("remove_habit:"))
async def remove_habit_callback(callback: CallbackQuery) -> None:
    habit_id = int(callback.data.split(":")[1])
    await db.remove_habit(callback.from_user.id, habit_id)
    await callback.message.edit_text("Habit removed 🌱")
    await callback.answer()


@router.callback_query(F.data == "cancel_remove")
async def cancel_remove(callback: CallbackQuery) -> None:
    await callback.message.edit_text("No changes made ✨")
    await callback.answer()


# ─── Weekly Progress ─────────────────────────────────────────────────────────

@router.message(F.text == "📈 Weekly Progress")
async def weekly_progress(message: Message) -> None:
    stats = await db.get_weekly_habit_stats(message.from_user.id)

    if not stats:
        await message.answer(
            "No habits tracked yet 🌱\nStart with Today's Habits!",
            reply_markup=habits_menu(),
        )
        return

    lines = ["🌱 <b>This Week</b>\n"]
    for s in stats:
        done = s["done"]
        bar = "█" * done + "░" * (7 - done)
        lines.append(f"{s['name']} — {done}/7  {bar}")

    total_done = sum(s["done"] for s in stats)
    total_possible = len(stats) * 7

    if total_done == total_possible:
        lines.append("\nPerfect week ✨ Absolutely beautiful.")
    elif total_done >= total_possible * 0.7:
        lines.append("\nBeautiful consistency this week ✨")
    elif total_done >= total_possible * 0.4:
        lines.append("\nSolid effort 🌱 Keep going.")
    else:
        lines.append("\nEvery small step still counts 🌱")

    await message.answer("\n".join(lines), reply_markup=habits_menu(), parse_mode="HTML")


# ─── Habit Reminder ──────────────────────────────────────────────────────────

@router.message(F.text == "⏰ Habit Reminder")
async def habit_reminder_settings(message: Message) -> None:
    user_settings = await db.get_user_settings(message.from_user.id)
    enabled = bool(user_settings.get("habit_reminder", 1))

    status = "on 🔔" if enabled else "off 🔕"
    await message.answer(
        f"Habit reminder is currently <b>{status}</b>\n\n"
        "If no habits are done by evening, I'll send a gentle nudge 🌱",
        reply_markup=habit_reminder_inline(enabled),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("reminder:habit:"))
async def toggle_habit_reminder(callback: CallbackQuery) -> None:
    action = callback.data.split(":")[-1]
    new_value = 1 if action == "on" else 0
    await db.update_user_setting(callback.from_user.id, "habit_reminder", new_value)

    status = "enabled 🔔" if new_value else "disabled 🔕"
    await callback.message.edit_text(
        f"Habit reminder {status} ✨",
        reply_markup=habit_reminder_inline(bool(new_value)),
    )
    await callback.answer()


# ─── Daily Reflection ────────────────────────────────────────────────────────

@router.message(F.text == "🌙 Daily Reflection")
async def daily_reflection(message: Message) -> None:
    await message.answer(
        "🌙 How did today feel?",
        reply_markup=reflection_inline(),
    )


@router.callback_query(F.data.startswith("mood:"))
async def receive_mood(callback: CallbackQuery) -> None:
    mood = callback.data.split(":")[1]
    await db.save_reflection(callback.from_user.id, mood)

    response = mood_responses.get(mood, "Thanks for sharing 🌙")
    await callback.message.edit_text(response)
    await callback.answer()


# ─── Back ─────────────────────────────────────────────────────────────────────

@router.message(F.text == "⬅ Back")
async def go_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Back to the main space 🌱", reply_markup=main_menu())
