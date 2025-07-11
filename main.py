import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os


load_dotenv('token.env')
# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот на aiogram.')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())