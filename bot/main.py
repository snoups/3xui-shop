import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers import main_menu
from bot.utils.config import config
from bot.utils.logger import Logger

logger: Logger = Logger("bot").get_logger()
aiogram_logger: Logger = Logger("aiogram")

bot: Bot = Bot(token=config.bot.token)
dp: Dispatcher = Dispatcher()


async def main() -> None:
    logger.info("Bot is starting...")

    main_menu.register_handler(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
