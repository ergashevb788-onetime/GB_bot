"""
utils/jokes.py — Wholesome jokes: programming, book, and general cute ones.
"""

import random

JOKES = [
    # Programming jokes
    ("Why do programmers prefer dark mode?", "Because light attracts bugs 🐛"),
    ("How many programmers does it take to change a light bulb?", "None — that's a hardware problem 💡"),
    ("Why do Java developers wear glasses?", "Because they don't C# 😄"),
    ("A SQL query walks into a bar, walks up to two tables and asks...", "\"Can I join you?\" 🍵"),
    ("Why did the developer go broke?", "Because they used up all their cache 😅"),
    ("What's a computer's favourite snack?", "Microchips 🍟"),
    ("Why do programmers always mix up Christmas and Halloween?", "Because Oct 31 == Dec 25 🎃"),
    ("I would tell you a UDP joke...", "...but you might not get it 😌"),

    # Book jokes
    ("What do you call a book club that's been stuck on one book for years?", "A cult 📚"),
    ("Why did the library book go to the doctor?", "Because it had too many problems 📖"),
    ("I tried writing a book about clocks...", "It was very time-consuming ⏰"),
    ("Why don't books ever win at poker?", "Because they always show their cover 🃏"),

    # Cute / general
    ("What do you call a fish without eyes?", "A fsh 🐟"),
    ("Why can't you give Elsa a balloon?", "She'll let it go 🎈"),
    ("I told my cat a joke. He didn't laugh...", "He's a tough crowd 🐱"),
    ("What do you call cheese that isn't yours?", "Nacho cheese 🧀"),
    ("Why did the scarecrow win an award?", "He was outstanding in his field 🌾"),
]


def get_random_joke() -> str:
    setup, punchline = random.choice(JOKES)
    return f"{setup}\n\n{punchline}"
