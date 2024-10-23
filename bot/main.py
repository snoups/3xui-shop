import asyncio

from aiogram import Bot, Dispatcher

from database.session import init_db
from handlers import main_menu, profile
from middlewares.user_check import UserCheckMiddleware
from utils.api import api
from utils.config import config
from utils.logger import Logger

logger: Logger = Logger("bot").get_logger()
aiogram_logger: Logger = Logger("aiogram")
sqlalchemy_logger = Logger("sqlalchemy.engine")

bot: Bot = Bot(token=config.bot.token)
dp: Dispatcher = Dispatcher()


async def main() -> None:
    await init_db()

    logger.info("Bot is starting...")
    await api.login()

    dp.message.middleware(UserCheckMiddleware())
    main_menu.register_handler(dp)
    profile.register_handler(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
