from pyrogram import Client, filters
from pyrogram.types import Message
from ShrutiMusic import app  # aapke project ka import
import requests
import yt_dlp
import os
import asyncio


def get_video_info_allvideo(url: str):
    try:
        response = requests.post(
            "https://allvideodownloader.cc/wp-json/aio-dl/video-data/",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0",
            },
            data={
                "url": url,
                "token": "c99f113fab0762d216b4545e5c3d615eefb30f0975fe107caab629d17e51b52d",
            },
            timeout=15,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        media = max(data["medias"], key=lambda x: int(x["quality"].replace("p", "")))
        return {
            "title": data["title"],
            "url": media["url"]
        }
    except:
        return None


async def download_video_ytdlp(url: str, file_name="ytvideo.mp4"):
    try:
        ydl_opts = {
            'outtmpl': file_name,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return file_name
    except Exception as e:
        return None


@app.on_message(filters.command("vid") & filters.private)
async def video_downloader(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "❌ Please provide a video URL.\n\nExample:\n/vid any_video_url",
            quote=True
        )

    url = message.text.split(None, 1)[1]
    msg = await message.reply("🔍 Processing your request...")

    filename = "video.mp4"
    title = ""

    # Try with allvideodownloader.cc
    info = get_video_info_allvideo(url)
    if info:
        try:
            title = info["title"]
            video_data = requests.get(info["url"], stream=True, timeout=10)
            total_length = int(video_data.headers.get('content-length', 0))
            if total_length == 0:
                raise Exception("Zero size")

            with open(filename, "wb") as f:
                for chunk in video_data.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
        except:
            info = None  # fallback to yt-dlp

    # Fallback to yt-dlp (for YouTube etc)
    if not info:
        await msg.edit("⚠️ Trying fallback method for YouTube...")
        downloaded = await download_video_ytdlp(url, filename)
        if not downloaded:
            return await msg.edit("❌ Failed to download the video using any method.")
        title = "Downloaded via yt-dlp"

    # Send the video
    try:
        await msg.edit("📤 Sending video...")
        await message.reply_video(
            video=filename,
            caption=f"🎬 <b>{title}</b>\n\n✅ By @ShrutiBots",
            quote=True
        )
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
