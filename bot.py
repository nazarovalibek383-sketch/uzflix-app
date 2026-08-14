import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8830005964:AAFU5_rFY0fvkQJi-AIpRbzFosSOvH_vFRQ"
WEB_APP_URL = "https://nazarovalibek383-sketch.github.io/uzflix-app/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 UzFlix App-ni ochish",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    await message.answer("Xush kelibsiz! UzFlix kinoteatrini ochish uchun pastdagi tugmani bosing:", reply_markup=kb)

async def main():
    logging.basicConfig(level=logging.INFO)
    # ESKI WEBHOOK'NI O'CHIRISH (Xatolikni yo'qotadi):
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
