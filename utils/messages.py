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
    "I think it's a little too early for that 🌙",
    
    "Maybe one day))) ",
    
    "People say a person needs at least 5 hugs a day to stay healthy.\nI'm clearly not a very healthy person 😂",
    
    "The same here).",
    
    "Patience is a beautiful thing 🌱",
    
    "I'm waiting for that day too ... ",
    
    "Virtual hugs are all I can offer for now) ",
    
    "One day, maybe.",
    
    "Still buffering that feature...",
    
    "This button comes with emotional damage included :) ",
    
    "Pending delivery...",
    
    "I'd say yes if Telegram allowed it :) ",
]

# ─── Comfort Messages ────────────────────────────────────────────────────────

comfort_messages = [
    "In a room full of art, I would still look at you.",

    "I passed by many eyes, but I only got lost in yours.",

    "If you remember me, then I don’t care if everyone else forgets.",

    "If I had a flower for every time I thought of you, I could walk through my garden forever.",

    "Once upon a time, there was a boy who loved a girl, and her laughter was a question he wanted to spend his whole life answering.",

    "Math is so confusing. It only talks about X and Y, but never U and I.",

    "My heart missed you.",

    "I know what love is because of you.",

    "On the train, we swapped seats. You wanted the window, and I wanted to look at you.",

    "I closed my mouth and talked to you in hundreds of silent ways.",

    "There are hundreds of ways to say 'I missed you' without using words.",

    "The window view was beautiful.\nStill not as distracting as you.",

    "Sometimes I reread old conversations just to smile again.",
]

# ─── Helper functions ─────────────────────────────────────────────────────────

def random_hug() -> str:
    return random.choice(hug_messages)

def random_comfort() -> str:
    return random.choice(comfort_messages)
