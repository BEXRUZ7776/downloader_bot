import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiohttp import web

# TOKENNI TO'G'RI YOZILGANINI TEKSHIRING
API_TOKEN = '8194455415:AAGZzZ_Yt3L09iP0068V_vHclY-2B8E6F0o'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def handle(request):
    return web.Response(text="Bot is running!")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Bot Render-da ishladi!")

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get("/", handle)
    loop = asyncio.get_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    loop.create_task(site.start())
    executor.start_polling(dp, skip_updates=True)
    
