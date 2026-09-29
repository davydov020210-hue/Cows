import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from func import *
from game import *
from admin import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token="8769780535:AAGa3m15uSR7IYa_U74OLVUHUNjKZabGUiM")
dp = Dispatcher()

async def periodic_task():
    while True:
        now = time.time()

        seconds_passed_this_hour = now % 3600
        seconds_to_wait = 3600 - seconds_passed_this_hour

        await asyncio.sleep(seconds_to_wait)

        change_milk_price()

async def main():
    asyncio.create_task(periodic_task())
    dp.include_router(game_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())