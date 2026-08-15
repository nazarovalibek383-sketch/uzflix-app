import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import firebase_admin
from firebase_admin import credentials, firestore

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8830005964:AAFU5_rFY0fvkQJi-AIpRbzFosSOvH_vFRQ"
WEB_APP_URL = "https://nazarovalibek383-sketch.github.io/uzflix-app/"
ADMIN_ID = 8892454236

# Firebase ulash
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==================== FSM (FORMA HOLATLARI) ====================
class AddContent(StatesGroup):
    category = State()
    title = State()
    description = State()
    poster = State()
    video_url = State()

class Broadcast(StatesGroup):
    message = State()

# ==================== KLAVIATURALAR ====================
def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Kino qo'shish"), KeyboardButton(text="📺 Serial qo'shish")],
            [KeyboardButton(text="🧸 Multfilm qo'shish"), KeyboardButton(text="🌀 Multserial qo'shish")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📢 Reklama yuborish")]
        ],
        resize_keyboard=True
    )

# ==================== FOYDALANUVCHI BO'LIMI ====================
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    # Foydalanuvchini bazaga saqlash
    user_ref = db.collection("users").document(str(message.from_user.id))
    if not user_ref.get().exists:
        user_ref.set({"user_id": message.from_user.id, "first_name": message.from_user.first_name})

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
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\nUzFlix kinoteatriga xush kelibsiz. Ilovani ochish uchun tugmani bosing:",
        reply_markup=kb
    )

# ==================== ADMIN PANEL ====================
@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin panelga xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=admin_keyboard())
    else:
        await message.answer("Siz admin emassiz!")

# 1. KONTENT QO'SHISH BOSHI
@dp.message(F.text.in_({"🎬 Kino qo'shish", "📺 Serial qo'shish", "🧸 Multfilm qo'shish", "🌀 Multserial qo'shish"}))
async def start_add_content(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    category_map = {
        "🎬 Kino qo'shish": "kino",
        "📺 Serial qo'shish": "serial",
        "🧸 Multfilm qo'shish": "multfilm",
        "🌀 Multserial qo'shish": "multserial"
    }
    
    await state.update_data(category=category_map[message.text])
    await state.set_state(AddContent.title)
    await message.answer("Sarlavhani (nomini) kiriting:")

@dp.message(AddContent.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddContent.description)
    await message.answer("Tavsif (Bio / qisqacha ma'lumot) kiriting:")

@dp.message(AddContent.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddContent.poster)
    await message.answer("Poster (rasm) havolasini (URL) kiriting:")

@dp.message(AddContent.poster)
async def process_poster(message: types.Message, state: FSMContext):
    await state.update_data(poster=message.text)
    await state.set_state(AddContent.video_url)
    await message.answer("Video havolasini (URL) kiriting:")

@dp.message(AddContent.video_url)
async def process_video_url(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    # Firebase Firestore'ga saqlash
    db.collection("movies").add({
        "category": data["category"],
        "title": data["title"],
        "description": data["description"],
        "poster": data["poster"],
        "videoUrl": message.text
    })
    
    await state.clear()
    await message.answer(f"✅ **{data['title']}** bazaga muvaffaqiyatli qo'shildi!", reply_markup=admin_keyboard())

# 2. STATISTIKA
@dp.message(F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users_count = len(list(db.collection("users").stream()))
    movies_count = len(list(db.collection("movies").stream()))
    
    await message.answer(
        f"📊 **Statistika:**\n\n"
        f"👤 Jami foydalanuvchilar: **{users_count}** ta\n"
        f"🎬 Jami yuklangan kontentlar: **{movies_count}** ta"
    )

# 3. REKLAMA (XABAR YUBORISH)
@dp.message(F.text == "📢 Reklama yuborish")
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.set_state(Broadcast.message)
    await message.answer("Barcha foydalanuvchilarga yuboriladigan xabar (reklama) matnini kiriting:")

@dp.message(Broadcast.message)
async def process_broadcast(message: types.Message, state: FSMContext):
    users = db.collection("users").stream()
    count = 0
    
    for u in users:
        try:
            user_data = u.to_dict()
            await bot.send_message(chat_id=user_data["user_id"], text=message.text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
            
    await state.clear()
    await message.answer(f"📢 Reklama **{count}** ta foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=admin_keyboard())

# ==================== MAIN RUN ====================
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
