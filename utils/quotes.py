"""
utils/quotes.py — Curated list of book, philosophy, and calm quotes.
"""

import random

QUOTES = [
    # Literature
    ("A reader lives a thousand lives before he dies. The man who never reads lives only one.", "George R.R. Martin"),
    ("Not all those who wander are lost.", "J.R.R. Tolkien"),
    ("We accept the love we think we deserve.", "Stephen Chbosky"),
    ("It does not do to dwell on dreams and forget to live.", "J.K. Rowling"),
    ("There is no friend as loyal as a book.", "Ernest Hemingway"),
    ("One must always be careful of books, and what is inside them.", "Cassandra Clare"),
    ("I am not afraid of storms, for I am learning how to sail my ship.", "Louisa May Alcott"),
    ("Books are mirrors: we see only what we already have inside us.", "Carlos Ruiz Zafón"),

    # Philosophy
    ("The impediment to action advances action. What stands in the way becomes the way.", "Marcus Aurelius"),
    ("It is not the man who has too little, but the man who craves more, that is poor.", "Seneca"),
    ("We suffer more in imagination than in reality.", "Seneca"),
    ("Waste no more time arguing about what a good man should be. Be one.", "Marcus Aurelius"),
    ("Knowing yourself is the beginning of all wisdom.", "Aristotle"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),

    # Calm & Motivational
    ("Your pace is still progress.", None),
    ("Small consistent steps matter more than perfect days.", None),
    ("Rest is not giving up. Rest is getting ready.", None),
    ("You don't have to be perfect to be worthy.", None),
    ("It's okay to not be okay. It's not okay to stay that way.", None),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
    ("The only way out of the labyrinth of suffering is to forgive.", "John Green"),
    ("Some books should be tasted, some devoured, but only a few should be chewed and digested thoroughly.", "Francis Bacon"),
    ("You are never too old to set another goal or dream a new dream.", "C.S. Lewis"),
    ("The more that you read, the more things you will know.", "Dr. Seuss"),
]


def get_random_quote() -> str:
    text, author = random.choice(QUOTES)
    if author:
        return f'"{text}"\n\n— {author} ✨'
    return f'"{text}" ✨'
