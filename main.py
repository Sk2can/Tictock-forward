import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
import yt_dlp
import tempfile
import re
import os


if load_dotenv('token.env'):
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
else:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция проверки доступности веб-страницы
async def is_url_accessible(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                return response.status == 200
    except Exception:
        return False

# Обработка команды /start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот для переслки тикток видео в укаазанную группу.')

# Обработка полученных сообщений от пользователя
@dp.message()
async def message_catch(message: types.Message):
    if re.search(r"^https://vt\.tiktok\.com/.*$", message.text) and await is_url_accessible(message.text):
        await download_and_send_video(message, message.text)

async def download_and_send_video(message, url):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'format': 'best[height<=720][ext=mp4]/mp4[height<=720]/best[ext=mp4]/mp4/best',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            # Проверяем расширение файла, если не mp4 — перекодируем
            if not video_path.lower().endswith('.mp4'):
                mp4_path = os.path.splitext(video_path)[0] + '.mp4'
                import subprocess
                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-i', video_path,
                    '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
                    '-movflags', '+faststart', mp4_path
                ]
                subprocess.run(ffmpeg_cmd, check=True)
                video_path = mp4_path

            # Получаем информацию о видео
            duration = info.get('duration', 0)
            width = info.get('width', 0)
            height = info.get('height', 0)

            # Создаем FSInputFile с правильными параметрами для видео
            video_file = FSInputFile(video_path)

            # Отправляем видео в группу как видео (не как файл)
            await bot.send_video(
                chat_id=GROUP_CHAT_ID,
                video=video_file,
                duration=duration,
                width=width,
                height=height,
                caption=f"Видео от @{message.from_user.username or message.from_user.first_name}",
                supports_streaming=True
            )

    except Exception as e:
        await message.answer(f"Ошибка при обработке видео: {str(e)}")
        # Файл будет удалён автоматически при выходе из блока with

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
