import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, executor, types

# Bot tokeningizni tekshiring
API_TOKEN = '8194455415:AAGZzZ_Yt3L09iP0068V_vHclY-2B8E6F0o'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Vaziyat nazorat ostida! Bot Render-da ishladi. ✅")

if __name__ == '__main__':
    # Flaskni alohida oqimda yuritamiz
    threading.Thread(target=run_flask).start()
    # Botni ishga tushiramiz
    executor.start_polling(dp, skip_updates=True)
    
