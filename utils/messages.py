"""
utils/messages.py — All bot messages in one place.
Warm, minimal, human. Never robotic.
"""

import random

# ─── Reading Reminders ────────────────────────────────────────────────────────

reading_reminder_messages = [
    "I know university gets busy sometimes 🌱 Maybe read even a few pages tonight?",
    "Your book is waiting for you quietly 📖",
    "Stories stay patient. Continue when you're ready ✨",
    "Even two pages count. Your book misses you 🌙",
    "A quiet moment with a book might be exactly what you need right now 📖",
    "No pressure — but your bookmark is still there, waiting 🌱",
]

# ─── Habit Reminders ─────────────────────────────────────────────────────────

habit_reminder_messages = [
    "Even one completed habit today is still progress 🌱",
    "Small steps still count ✨",
    "Hey — there's still time for one small thing tonight 🌙",
    "A tiny bit of consistency beats a perfect day that never comes 🌱",
    "One habit. That's all. You've got this ✨",
]

# ─── Reading Progress Responses ───────────────────────────────────────────────

def reading_progress_response(pages: int) -> str:
    if pages == 0:
        return "Page noted 🌱 Every update counts."
    elif pages <= 5:
        return f"Quiet progress still counts ✨ ({pages} pages)"
    elif pages <= 15:
        return f"Nice 🌱 You read {pages} pages today."
    elif pages <= 30:
        return f"That's a lovely session 📖 {pages} pages — well done."
    else:
        return f"Wow, {pages} pages! You really got lost in your book today ✨"


# ─── Mood Responses ───────────────────────────────────────────────────────────

mood_responses = {
    "good":   "Really glad to hear that 😊 Keep the warmth with you.",
    "calm":   "Calm days are quietly beautiful 😌 Rest well tonight.",
    "tiring": "Tired days count too 🌱 Hope tomorrow feels lighter ✨",
    "busy":   "Busy days count too 🌱 You showed up anyway — that matters.",
}

# ─── Hug Messages ────────────────────────────────────────────────────────────

hug_messages = [
    "Sending a warm virtual hug 🌙",
    "You're doing better than you think ✨",
    "Rest a little too 🌱",
    "You're not alone in this. Keep going, gently 🤍",
    "It's okay to be tired. You're still here ✨",
    "Proud of you for every small thing today 🌙",
    "One day at a time. You're doing it 🌱",
]

# ─── Comfort Messages ────────────────────────────────────────────────────────

comfort_messages = [
    "Your pace is still progress.",
    "One difficult day doesn't define you.",
    "Drink some water and continue slowly 🌱",
    "Small consistent steps matter more than perfect days 🌱",
    "You don't have to have it all figured out today ✨",
    "Rest is also part of the process 🌙",
    "Being kind to yourself is productive too.",
    "It's okay if today was just surviving. That counts 🌱",
    "Tomorrow is a fresh page ✨",
    "You showed up. That's already something.",
]

# ─── Helper functions ─────────────────────────────────────────────────────────

def random_hug() -> str:
    return random.choice(hug_messages)

def random_comfort() -> str:
    return random.choice(comfort_messages)
