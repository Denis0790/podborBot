import asyncio
from aiogram import Bot, Dispatcher
from app.handler_answer_user import router_answer_user
from app.handlers import router

from env import TOKEN

bot = Bot(TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router_answer_user)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
