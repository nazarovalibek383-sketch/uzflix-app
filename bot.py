import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

BOT_TOKEN = "8830005964:AAFU5_rFY0fvkQJi-AIpRbzFosSOvH_vFRQ"
WEB_APP_URL = "https://nazarovalibek383-sketch.github.io/uzflix-app/"
ADMIN_ID = 8892454236

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Foydalanuvchilar bazasi (Test uchun to'plam)
users_db = set()


# FSM States (Reklama uchun)
class AdminStates(StatesGroup):
    waiting_for_ad = State()


# /start buyrug'i
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    users_db.add(message.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Kinolarni onlayn ko'rish",
                    web_app=WebAppInfo(url=WEB_APP_URL),
                )
            ]
        ]
    )

    await message.answer(
        f"Salom, {message.from_user.first_name}!\n\n"
        "UzFlix kinoteatriga xush kelibsiz. Barcha kinolarni bot ichida onlayn tomosha qilishingiz mumkin:",
        reply_markup=keyboard,
    )


# Admin Paneli
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    admin_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistika", callback_data="stat"
                ),
                InlineKeyboardButton(
                    text="📢 Reklama joylash", callback_data="send_ad"
                ),
            ]
        ]
    )

    await message.answer("🛠 Admin Paneli:", reply_markup=admin_keyboard)


# Statistika
@dp.callback_query(F.data == "stat")
async def show_stats(callback: types.CallbackQuery):
    await callback.message.answer(
        f"📊 **Bot Statistikasi:**\n\n"
        f"👤 Jami obunachilar: {len(users_db)} ta"
    )
    await callback.answer()


# Reklama yuborishni boshlash
@dp.callback_query(F.data == "send_ad")
async def start_ad(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📢 Reklama xabarini (matn, rasm yoki video) yuboring:"
    )
    await state.set_state(AdminStates.waiting_for_ad)
    await callback.answer()


# Reklamani barchaga tarqatish
@dp.message(AdminStates.waiting_for_ad)
async def process_ad(message: types.Message, state: FSMContext):
    count = 0
    for user_id in users_db:
        try:
            await message.copy_to(chat_id=user_id)
            count += 1
        except Exception:
            pass

    await message.answer(f"✅ Reklama {count} ta obunachiga yuborildi!")
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
