"""
scheduler.py — APScheduler setup for reading and habit reminders.

Checks run once daily in the evening.
Reminders are gentle and non-spammy — one per trigger condition.
"""

import logging
from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database as db
from utils.messages import reading_reminder_messages, habit_reminder_messages
import random

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()


def setup_scheduler(bot: Bot) -> None:
    """Register scheduled jobs and start the scheduler."""

    # Reading reminder: runs at 21:00 every day
    _scheduler.add_job(
        check_reading_reminders,
        trigger="cron",
        hour=21,
        minute=0,
        kwargs={"bot": bot},
        id="reading_reminder",
        replace_existing=True,
    )

    # Habit reminder: runs at 20:00 every day
    _scheduler.add_job(
        check_habit_reminders,
        trigger="cron",
        hour=20,
        minute=0,
        kwargs={"bot": bot},
        id="habit_reminder",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started 🌱")


async def check_reading_reminders(bot: Bot) -> None:
    """
    Send a gentle reminder to users who haven't read in 2+ days
    and have reminders enabled.
    """
    users = await db.get_all_users()
    now = datetime.now()

    for user in users:
        uid = user["user_id"]
        try:
            user_settings = await db.get_user_settings(uid)
            if not user_settings.get("reading_reminder", 1):
                continue

            last_activity = await db.get_last_reading_activity(uid)

            # Only remind if inactive for 2+ days (or never read)
            if last_activity is None or (now - last_activity) >= timedelta(days=2):
                msg = random.choice(reading_reminder_messages)
                await bot.send_message(uid, msg)
                logger.info(f"Reading reminder sent to {uid}")

        except Exception as e:
            # Never crash the scheduler over one user
            logger.warning(f"Reading reminder failed for {uid}: {e}")


async def check_habit_reminders(bot: Bot) -> None:
    """
    Send a gentle nudge to users who haven't completed any habit today
    and have reminders enabled.
    """
    users = await db.get_all_users()

    for user in users:
        uid = user["user_id"]
        try:
            user_settings = await db.get_user_settings(uid)
            if not user_settings.get("habit_reminder", 1):
                continue

            any_done = await db.any_habit_completed_today(uid)
            if not any_done:
                msg = random.choice(habit_reminder_messages)
                await bot.send_message(uid, msg)
                logger.info(f"Habit reminder sent to {uid}")

        except Exception as e:
            logger.warning(f"Habit reminder failed for {uid}: {e}")
