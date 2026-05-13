"""
database.py — PostgreSQL database layer using asyncpg.

Migrated from SQLite + aiosqlite.
All function signatures and return types are IDENTICAL to the original —
handlers require zero changes.

Key differences from SQLite version:
  - Uses a shared asyncpg connection pool (created once at startup)
  - Placeholders are $1, $2, ... instead of ?
  - AUTOINCREMENT  →  SERIAL
  - datetime('now') →  CURRENT_TIMESTAMP
  - date(column)   →  column::date
  - SQLite integer booleans → native PostgreSQL BOOLEAN
  - toggle_habit uses clean check + update pattern
"""

import asyncpg
import logging
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Connection pool (module-level, initialised in init_db) ──────────────────
_pool: asyncpg.Pool | None = None


def _get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError(
            "Database pool is not initialised. "
            "Make sure init_db() is awaited at bot startup."
        )
    return _pool


# ─── Init ─────────────────────────────────────────────────────────────────────

async def init_db() -> None:
    """Create the connection pool and all tables (idempotent)."""
    global _pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL is missing. Add it to your .env or Render dashboard."
        )

    # Render gives 'postgres://' but asyncpg needs 'postgresql://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    _pool = await asyncpg.create_pool(
        dsn=database_url,
        min_size=1,
        max_size=10,
        command_timeout=30,
        ssl="require",
    )

    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     BIGINT PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                created_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS books (
                id           SERIAL PRIMARY KEY,
                user_id      BIGINT NOT NULL REFERENCES users(user_id),
                title        TEXT NOT NULL,
                author       TEXT,
                current_page INTEGER DEFAULT 0,
                total_pages  INTEGER,
                status       TEXT DEFAULT 'reading',
                started_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                finished_at  TIMESTAMPTZ
            );

            CREATE TABLE IF NOT EXISTS reading_logs (
                id          SERIAL PRIMARY KEY,
                user_id     BIGINT NOT NULL REFERENCES users(user_id),
                book_id     INTEGER REFERENCES books(id),
                pages_read  INTEGER NOT NULL,
                logged_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS quotes (
                id          SERIAL PRIMARY KEY,
                user_id     BIGINT NOT NULL REFERENCES users(user_id),
                text        TEXT NOT NULL,
                book_name   TEXT,
                saved_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS habits (
                id          SERIAL PRIMARY KEY,
                user_id     BIGINT NOT NULL REFERENCES users(user_id),
                name        TEXT NOT NULL,
                emoji       TEXT DEFAULT '✨',
                created_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS habit_logs (
                id          SERIAL PRIMARY KEY,
                habit_id    INTEGER NOT NULL REFERENCES habits(id),
                user_id     BIGINT NOT NULL REFERENCES users(user_id),
                completed   BOOLEAN DEFAULT FALSE,
                log_date    DATE NOT NULL,
                UNIQUE (habit_id, log_date)
            );

            CREATE TABLE IF NOT EXISTS reflections (
                id          SERIAL PRIMARY KEY,
                user_id     BIGINT NOT NULL REFERENCES users(user_id),
                mood        TEXT NOT NULL,
                logged_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                user_id          BIGINT PRIMARY KEY REFERENCES users(user_id),
                reading_reminder BOOLEAN DEFAULT TRUE,
                habit_reminder   BOOLEAN DEFAULT TRUE
            );
            CREATE TABLE IF NOT EXISTS little_things_logs (
                id         SERIAL PRIMARY KEY,
                user_id    BIGINT NOT NULL REFERENCES users(user_id),
                action     TEXT NOT NULL,
                logged_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
           );
        """)

    logger.info("Database initialised ✨")


async def close_db() -> None:
    """Gracefully close the pool on bot shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed 🌙")


# ─── Users ────────────────────────────────────────────────────────────────────

async def get_or_create_user(user_id: int, username: str, first_name: str) -> None:
    """Ensure the user exists; create default habits on first visit."""
    pool = _get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT user_id FROM users WHERE user_id = $1", user_id
        )

        if not existing:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO users (user_id, username, first_name) VALUES ($1, $2, $3)",
                    user_id, username, first_name,
                )
                await conn.execute(
                    "INSERT INTO settings (user_id) VALUES ($1)", user_id
                )
                default_habits = [
                    "📚 Reading",
                    "💻 Coding",
                    "💧 Water",
                    "🕌 Quran",
                    "🌙 Sleep Early",
                ]
                for name in default_habits:
                    await conn.execute(
                        "INSERT INTO habits (user_id, name) VALUES ($1, $2)",
                        user_id, name,
                    )


async def get_all_users() -> list[dict]:
    """Return all users (used by the scheduler)."""
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id, first_name FROM users")
        return [dict(r) for r in rows]


# ─── Books ────────────────────────────────────────────────────────────────────

async def get_current_book(user_id: int) -> dict | None:
    pool = _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM books WHERE user_id = $1 AND status = 'reading' "
            "ORDER BY started_at DESC LIMIT 1",
            user_id,
        )
        return dict(row) if row else None


async def add_book(user_id: int, title: str, total_pages: int | None = None) -> int:
    """Add a new book and return its id."""
    pool = _get_pool()
    async with pool.acquire() as conn:
        book_id = await conn.fetchval(
            "INSERT INTO books (user_id, title, total_pages) "
            "VALUES ($1, $2, $3) RETURNING id",
            user_id, title, total_pages,
        )
        return book_id


async def update_book_page(user_id: int, book_id: int, new_page: int) -> int:
    """Update current page; return pages read today (delta)."""
    pool = _get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT current_page FROM books WHERE id = $1 AND user_id = $2",
                book_id, user_id,
            )
            old_page = row["current_page"] if row else 0
            pages_read = max(0, new_page - old_page)

            await conn.execute(
                "UPDATE books SET current_page = $1 WHERE id = $2 AND user_id = $3",
                new_page, book_id, user_id,
            )

            if pages_read > 0:
                await conn.execute(
                    "INSERT INTO reading_logs (user_id, book_id, pages_read) "
                    "VALUES ($1, $2, $3)",
                    user_id, book_id, pages_read,
                )

    return pages_read


async def get_pages_read_today(user_id: int) -> int:
    today = date.today()
    pool = _get_pool()
    async with pool.acquire() as conn:
        val = await conn.fetchval(
            "SELECT COALESCE(SUM(pages_read), 0) FROM reading_logs "
            "WHERE user_id = $1 AND logged_at::date = $2",
            user_id, today,
        )
        return int(val or 0)


async def get_all_books(user_id: int) -> list[dict]:
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM books WHERE user_id = $1 ORDER BY started_at DESC",
            user_id,
        )
        return [dict(r) for r in rows]


async def get_last_reading_activity(user_id: int) -> datetime | None:
    """Returns the most recent reading log timestamp."""
    pool = _get_pool()
    async with pool.acquire() as conn:
        # asyncpg returns a real datetime object — no .fromisoformat() needed
        val = await conn.fetchval(
            "SELECT MAX(logged_at) FROM reading_logs WHERE user_id = $1", user_id
        )
        return val


async def finish_book(user_id: int, book_id: int) -> None:
    pool = _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE books SET status = 'finished', finished_at = CURRENT_TIMESTAMP "
            "WHERE id = $1 AND user_id = $2",
            book_id, user_id,
        )


# ─── Quotes ───────────────────────────────────────────────────────────────────

async def save_quote(user_id: int, text: str, book_name: str | None = None) -> None:
    pool = _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO quotes (user_id, text, book_name) VALUES ($1, $2, $3)",
            user_id, text, book_name,
        )


async def get_user_quotes(user_id: int) -> list[dict]:
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM quotes WHERE user_id = $1 ORDER BY saved_at DESC LIMIT 20",
            user_id,
        )
        return [dict(r) for r in rows]


# ─── Habits ───────────────────────────────────────────────────────────────────

async def get_user_habits(user_id: int) -> list[dict]:
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM habits WHERE user_id = $1 ORDER BY created_at",
            user_id,
        )
        return [dict(r) for r in rows]


async def get_habit_completions_today(user_id: int) -> dict[int, bool]:
    """Returns {habit_id: completed_bool} for today."""
    today = date.today()
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT habit_id, completed FROM habit_logs "
            "WHERE user_id = $1 AND log_date = $2",
            user_id, today,
        )
        return {r["habit_id"]: bool(r["completed"]) for r in rows}


async def toggle_habit(user_id: int, habit_id: int) -> bool:
    """Toggle today's habit completion. Returns the new state."""
    today = date.today()
    pool = _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT completed FROM habit_logs "
            "WHERE user_id = $1 AND habit_id = $2 AND log_date = $3",
            user_id, habit_id, today,
        )

        if row is None:
            await conn.execute(
                "INSERT INTO habit_logs (habit_id, user_id, completed, log_date) "
                "VALUES ($1, $2, TRUE, $3)",
                habit_id, user_id, today,
            )
            return True
        else:
            new_state = not bool(row["completed"])
            await conn.execute(
                "UPDATE habit_logs SET completed = $1 "
                "WHERE user_id = $2 AND habit_id = $3 AND log_date = $4",
                new_state, user_id, habit_id, today,
            )
            return new_state


async def add_habit(user_id: int, name: str) -> None:
    pool = _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO habits (user_id, name) VALUES ($1, $2)",
            user_id, name,
        )


async def remove_habit(user_id: int, habit_id: int) -> None:
    pool = _get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Delete logs first (foreign key)
            await conn.execute(
                "DELETE FROM habit_logs WHERE habit_id = $1 AND user_id = $2",
                habit_id, user_id,
            )
            await conn.execute(
                "DELETE FROM habits WHERE id = $1 AND user_id = $2",
                habit_id, user_id,
            )


async def get_weekly_habit_stats(user_id: int) -> list[dict]:
    """Returns habit name + completion count for the past 7 days."""
    since = date.today() - timedelta(days=6)
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT h.name,
                   COALESCE(SUM(CASE WHEN hl.completed THEN 1 ELSE 0 END), 0) AS done
            FROM habits h
            LEFT JOIN habit_logs hl
                   ON h.id = hl.habit_id
                  AND hl.log_date >= $1
            WHERE h.user_id = $2
            GROUP BY h.id, h.name, h.created_at
            ORDER BY h.created_at
            """,
            since, user_id,
        )
        return [dict(r) for r in rows]


async def any_habit_completed_today(user_id: int) -> bool:
    today = date.today()
    pool = _get_pool()
    async with pool.acquire() as conn:
        val = await conn.fetchval(
            "SELECT 1 FROM habit_logs WHERE user_id = $1 "
            "AND log_date = $2 AND completed = TRUE LIMIT 1",
            user_id, today,
        )
        return val is not None


# ─── Reflections ─────────────────────────────────────────────────────────────

async def save_reflection(user_id: int, mood: str) -> None:
    pool = _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO reflections (user_id, mood) VALUES ($1, $2)",
            user_id, mood,
        )


# ─── Settings ─────────────────────────────────────────────────────────────────

async def get_user_settings(user_id: int) -> dict:
    pool = _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM settings WHERE user_id = $1", user_id
        )
        if row:
            return dict(row)
        return {"reading_reminder": True, "habit_reminder": True}


async def update_user_setting(user_id: int, key: str, value: int) -> None:
    """key must be 'reading_reminder' or 'habit_reminder'. value is 0 or 1."""
    allowed_keys = {"reading_reminder", "habit_reminder"}
    if key not in allowed_keys:
        raise ValueError(f"Invalid settings key: {key!r}")

    pool = _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE settings SET {key} = $1 WHERE user_id = $2",
            bool(value), user_id,
        )

async def log_little_thing(user_id: int, action: str) -> None:
    """Silently log a Little Things interaction. Never raises."""
    try:
        pool = _get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO little_things_logs (user_id, action) VALUES ($1, $2)",
                user_id, action,
            )
    except Exception as e:
        logger.warning(f"little_things log failed: {e}")

  
