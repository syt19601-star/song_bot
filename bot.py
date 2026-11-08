import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from shazamio import Shazam


# ضع توكن البوت الخاص بك هنا بين علامتي التنصيص
TOKEN = "9064036231:AAHtb6MkWewNyfM7Ur2qDgvK_ZrVC_9ov6c"

bot = Bot(token=TOKEN)
dp = Dispatcher()
shazam = Shazam()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "أهلاً بك! 🎵\nأرسل لي أي مقطع صوتي أو فيديو، وسأقوم بالبحث عن اسم الأغنية المستخدمة فيه."
    )

@dp.message(lambda msg: msg.audio or msg.video or msg.document or msg.voice)
async def handle_media(message: types.Message):
    await message.answer("🔍 جاري تحميل الملف ومعالجة الصوت، ثوانٍ معدودة...")

    try:
        media = message.audio or message.video or message.document or message.voice
        file_id = media.file_id

        file = await bot.get_file(file_id)
        file_path = file.file_path

        local_file = f"downloaded_{message.from_user.id}.mp3"
        await bot.download_file(file_path, local_file)

        out = await shazam.recognize(local_file)

        if os.path.exists(local_file):
            os.remove(local_file)

        if "track" in out:
            track = out["track"]
            title = track.get("title", "غير معروف")
            artist = track.get("subtitle", "فنان غير معروف")
            hub = track.get("hub", {})
            actions = hub.get("actions", {})

            track_url = ""
            for action in actions:
                if "uri" in action:
                    track_url = action["uri"]
                    break

            response_text = f"✨ **تم العثور على الأغنية!**\n\n" \
                            f"🎵 **الاسم:** {title}\n" \
                            f"🎤 **المطرب/الفنان:** {artist}"

            if track_url:
                response_text += f"\n🔗 [رابط الاستماع]({track_url})"

            await message.answer(response_text, parse_mode="Markdown")
        else:
            await message.answer("❌ عذراً، لم أستطع التعرف على الأغنية في هذا الملف. تأكد أن الصوت واضح.")

    except Exception as e:
        await message.answer(f"⚠️ حدث خطأ أثناء المعالجة: {str(e)}")

async def main():
    print("Bot is running...")
    await web_server()
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
  
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
