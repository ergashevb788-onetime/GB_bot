"""
bot.py — Entry point for the Cozy Productivity Bot
Handles startup, webhook setup, and graceful shutdown.
"""

import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import settings
from database import init_db, close_db
from scheduler import setup_scheduler
from handlers.start import router as start_router
from handlers.reading import router as reading_router
from handlers.habits import router as habits_router
from handlers.little_things import router as little_things_router

# Clean logging — no noise, just what matters
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Called when the bot starts up."""
    await init_db()
    logger.info("Database ready ✨")

    if settings.WEBHOOK_URL:
        webhook_path = f"/webhook/{settings.BOT_TOKEN}"
        full_url = f"{settings.WEBHOOK_URL}{webhook_path}"
        await bot.set_webhook(full_url, drop_pending_updates=True)
        logger.info(f"Webhook set → {full_url}")
    else:
        logger.info("Running in polling mode (no WEBHOOK_URL set)")


async def on_shutdown(bot: Bot) -> None:
    """Called when the bot shuts down."""
    if settings.WEBHOOK_URL:
        await bot.delete_webhook()
    await close_db()
    logger.info("Bot shut down gracefully 🌙")


def create_app() -> web.Application:
    """Build the aiohttp web application with webhook support."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Register all routers
    dp.include_router(start_router)
    dp.include_router(reading_router)
    dp.include_router(habits_router)
    dp.include_router(little_things_router)

    # Startup / shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Set up the scheduler (reminders)
    setup_scheduler(bot)

    app = web.Application()

    webhook_path = f"/webhook/{settings.BOT_TOKEN}"
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    return app


async def run_polling() -> None:
    """Run the bot in polling mode (for local development)."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(reading_router)
    dp.include_router(habits_router)
    dp.include_router(little_things_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    setup_scheduler(bot)

    logger.info("Starting polling mode 🌱")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    if settings.WEBHOOK_URL:
        # Production: webhook mode on Render
        app = create_app()
        web.run_app(app, host="0.0.0.0", port=settings.PORT)
    else:
        # Local dev: polling mode
        asyncio.run(run_polling())
