import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, executor, types

# Bot tokeningiz
API_TOKEN = '8194455415:AAGZzZ_Yt3L09iP0068V_vHclY-2B8E6F0o'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Render o'chib qolmasligi uchun Flask server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Bot buyruqlari
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bot Render-da muvaffaqiyatli ishga tushdi! ✅")

if __name__ == '__main__':
    # Flask serverni alohida oqimda ishga tushiramiz
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Botni ishga tushiramiz
    executor.start_polling(dp, skip_updates=True)
    
