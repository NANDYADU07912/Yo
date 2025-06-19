from pyrogram import filters
from pyrogram.types import Message
from ShrutiMusic import app
import requests

API_ENDPOINT = "https://allvideodownloader.cc/wp-json/aio-dl/video-data/"
API_TOKEN = "c99f113fab0762d216b4545e5c3d615eefb30f0975fe107caab629d17e51b52d"

@app.on_message(filters.command("vid") & filters.private)
async def video_downloader(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a video URL.\n\nExample:\n`/vid https://www.instagram.com/reel/xyz/`")

    video_url = message.text.split(None, 1)[1]

    msg = await message.reply("🔍 Fetching video link...")

    payload = {
        "url": video_url,
        "token": API_TOKEN
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14)",
        "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    }

    try:
        response = requests.post(API_ENDPOINT, data=payload, headers=headers, timeout=15)
        if response.status_code != 200:
            return await msg.edit(f"❌ API Error: {response.status_code}")

        data = response.json()

        if "medias" not in data or not data["medias"]:
            return await msg.edit("❌ No video found or unsupported format.")

        # Pick the best/highest quality video
        best_media = sorted(data["medias"], key=lambda x: x.get("quality", ""), reverse=True)[0]
        video_download_url = best_media["url"]

        await msg.edit("⬇️ Downloading & sending video...")

        await app.send_video(
            chat_id=message.chat.id,
            video=video_download_url,
            caption=f"🎬 <b>{data.get('title', 'Video')}</b>\n\n✅ Downloaded via @ShrutiBots",
            thumb=data.get("thumbnail"),
            supports_streaming=True
        )
        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
