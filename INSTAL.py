import os
import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp

# --- SOZLAMALAR ---
API_TOKEN = "8794455415:AAGvCP0i99O6RYy33jHqYa9ZagNd7SPghV8"
ADMIN_USERNAME = "@b_babaev"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- MA'LUMOTLAR BAZASI ---
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
# Bazaga 'lang' ustunini qo'shdik
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, lang TEXT DEFAULT 'uz')")
conn.commit()

def set_language(user_id, lang):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
    conn.commit()

def get_language(user_id):
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else "uz"

# --- MATNLAR ---
TEXTS = {
    "uz": {
        "start": "Salom! Video linkini yuboring.",
        "lang_select": "Tilni tanlang:",
        "format": "Formatni tanlang:",
        "wait": "⏳ Yuklanmoqda... Kuting...",
        "success": "Tayyor! ✅",
        "error": "Xatolik yuz berdi.",
        "admin": "👨‍💻 Adminga yozish"
    },
    "ru": {
        "start": "Привет! Отправьте ссылку на видео.",
        "lang_select": "Выберите язык:",
        "format": "Выберите формат:",
        "wait": "⏳ Загрузка... Пожалуйста, подождите...",
        "success": "Готово! ✅",
        "error": "Произошла ошибка.",
        "admin": "👨‍💻 Связаться с админом"
    },
    "en": {
        "start": "Hello! Send me a video link.",
        "lang_select": "Select language:",
        "format": "Select format:",
        "wait": "⏳ Downloading... Please wait...",
        "success": "Done! ✅",
        "error": "An error occurred.",
        "admin": "👨‍💻 Contact Admin"
    }
}

# --- TUGMALAR ---
def get_lang_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(text="🇺🇿 UZB", callback_data="setlang|uz"),
        types.InlineKeyboardButton(text="🇷🇺 RUS", callback_data="setlang|ru"),
        types.InlineKeyboardButton(text="🇺🇸 ENG", callback_data="setlang|en")
    )
    return keyboard

def get_download_menu(url, lang):
    keyboard = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton(text="🎬 Video (MP4)", callback_data=f"mp4|{url}")
    btn_audio = types.InlineKeyboardButton(text="🎵 Audio (MP3)", callback_data=f"mp3|{url}")
    btn_admin = types.InlineKeyboardButton(text=TEXTS[lang]["admin"], url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    
    keyboard.row(btn_video, btn_audio)
    keyboard.add(btn_admin)
    return keyboard

# --- YUKLASH FUNKSIYASI ---
def download_media(url, mode):
    filename = "result.mp3" if mode == "mp3" else "result.mp4"
    if os.path.exists(filename): os.remove(filename)
    ydl_opts = {'outtmpl': filename, 'max_filesize': 48 * 1024 * 1024, 'quiet': True}
    if mode == "mp3":
        ydl_opts['format'] = 'bestaudio/best'
    else:
        ydl_opts['format'] = 'best[ext=mp4]/best'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

# --- HANDLERLAR ---
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    lang = get_language(message.from_user.id)
    await message.answer(TEXTS[lang]["start"], reply_markup=get_lang_keyboard())

@dp.message_handler(commands=['lang'])
async def lang_cmd(message: types.Message):
    lang = get_language(message.from_user.id)
    await message.answer(TEXTS[lang]["lang_select"], reply_markup=get_lang_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('setlang|'))
async def set_lang_callback(callback: types.CallbackQuery):
    lang = callback.data.split("|")[1]
    set_language(callback.from_user.id, lang)
    await callback.answer("OK!")
    await bot.edit_message_text(TEXTS[lang]["start"], callback.message.chat.id, callback.message.message_id)

@dp.message_handler()
async def link_handler(message: types.Message):
    lang = get_language(message.from_user.id)
    if "http" in message.text:
        await message.answer(TEXTS[lang]["format"], reply_markup=get_download_menu(message.text, lang))
    else:
        await message.answer(TEXTS[lang]["start"])

@dp.callback_query_handler(lambda c: '|' in c.data and not c.data.startswith('setlang'))
async def download_callback(callback: types.CallbackQuery):
    lang = get_language(callback.from_user.id)
    mode, url = callback.data.split("|")
    
    if url == "none": return await callback.answer("!")

    status_msg = await bot.send_message(callback.message.chat.id, TEXTS[lang]["wait"])
    
    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_media, url, mode)
        
        with open(file_path, 'rb') as file:
            if mode == "mp3":
                await bot.send_audio(callback.message.chat.id, file, caption=TEXTS[lang]["success"])
            else:
                await bot.send_video(callback.message.chat.id, file, caption=TEXTS[lang]["success"])
            
        os.remove(file_path)
        await bot.delete_message(callback.message.chat.id, status_msg.message_id)
    except Exception as e:
        await bot.send_message(callback.message.chat.id, f"{TEXTS[lang]['error']}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
