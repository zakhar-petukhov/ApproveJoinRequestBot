import logging
import asyncio

import config
from admin.admin import admin_panel
from bot.bot import bot
from db.configure import configure_database
from parser.updater import DataUpdater

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for running the bot and the updater."""
    try:
        # Initialize database connection/configuration
        configure_database()

        # Register admin panel commands or logic
        admin_panel(bot)

        loop = asyncio.get_event_loop()
        # Start the bot
        logger.info("Starting bot")
        bot.start(bot_token=config.BOT_TOKEN)

        # Start periodic data updater
        logger.info("Starting updater")
        updater = DataUpdater(update_interval_seconds=300)
        loop.create_task(updater.start(), name="updater"),

        loop.run_forever()
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
