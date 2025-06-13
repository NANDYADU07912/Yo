import time
import asyncio
import random
from typing import Final

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from ShrutiMusic import app
from ShrutiMusic.misc import _boot_
from ShrutiMusic.plugins.sudo.sudoers import sudoers_list
from ShrutiMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from ShrutiMusic.utils import bot_sys_stats
from ShrutiMusic.utils.decorators.language import LanguageStart
from ShrutiMusic.utils.formatters import get_readable_time
from ShrutiMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# Success effect IDs to be randomly selected
SUCCESS_EFFECT_IDS: Final[list[str]] = [
    "5104841245755180586",  # 🔥
    "5107584321108051014",  # 👍
    "5046509860389126442",  # 🎉
    "5104858069142078462",  # 👎
    "5046589136895476101",  # 💩
]

# Special reaction effect IDs for animated reactions
REACTION_EFFECT_IDS: Final[list[str]] = [
    "5159385139981059251",  # Heart animation
    "5107584321108051014",  # Thumbs up animation
    "5046509860389126442",  # Party animation
    "5104841245755180586",  # Fire animation
    "5159394597140101489",  # Love animation
]

def get_random_effect_id():
    return int(random.choice(SUCCESS_EFFECT_IDS))

def get_random_reaction_effect_id():
    return int(random.choice(REACTION_EFFECT_IDS))

# Enhanced reaction function with animation effects
async def send_animated_reaction(message: Message, emoji: str = "🍓"):
    """Send big animated reaction"""
    try:
        # Method 1: Using send_reaction with big=True for animation
        await app.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=emoji,
            big=True  # This creates the big animated reaction!
        )
    except Exception as e:
        print(f"Big reaction failed, trying normal reaction: {e}")
        try:
            # Fallback to normal reaction
            await message.react(emoji)
        except Exception as e2:
            print(f"Normal reaction also failed: {e2}")
            
# Alternative method for better visual effects
async def send_reaction_with_effect(message: Message, emoji: str = "🍓"):
    """Send big reaction and follow with effect message"""
    try:
        # First send the big animated reaction
        await app.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=emoji,
            big=True  # Big animated reaction
        )
        
        # Optional: Add effect message for extra impact
        await asyncio.sleep(0.3)  # Small delay
        effect_msg = await app.send_message(
            chat_id=message.chat.id,
            text=f"✨",
            reply_to_message_id=message.id,
            message_effect_id=get_random_effect_id()
        )
        
        # Delete the effect message after 1.5 seconds
        await asyncio.sleep(1.5)
        try:
            await effect_msg.delete()
        except:
            pass
            
    except Exception as e:
        print(f"Big reaction with effect failed: {e}")
        try:
            # Fallback to simple reaction
            await message.react(emoji)
        except Exception as e2:
            print(f"Simple reaction also failed: {e2}")


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # 🍓 Big animated reaction
    await send_animated_reaction(message, "🍓")

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            try:
                return await app.send_photo(
                    chat_id=message.chat.id,
                    photo=config.START_IMG_URL,
                    caption=_["help_1"].format(config.SUPPORT_GROUP),
                    protect_content=True,
                    reply_markup=keyboard,
                    message_effect_id=get_random_effect_id()
                )
            except Exception:
                return await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["help_1"].format(config.SUPPORT_GROUP),
                    protect_content=True,
                    reply_markup=keyboard,
                )

        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} just started sudo check.\n"
                         f"User ID: <code>{message.from_user.id}</code>\n"
                         f"Username: @{message.from_user.username}",
                )
            return

        elif name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=_["S_B_8"], url=link),
                 InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP)],
            ])
            await m.delete()
            try:
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    caption=searched,
                    reply_markup=key,
                    message_effect_id=get_random_effect_id()
                )
            except Exception:
                await message.reply_photo(
                    photo=thumbnail,
                    caption=searched,
                    reply_markup=key,
                )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} requested track info.\n"
                         f"User ID: <code>{message.from_user.id}</code>\n"
                         f"Username: @{message.from_user.username}",
                )

    else:
        out = private_panel(_)
        UP, CPU, RAM, DISK = await bot_sys_stats()

        try:
            await app.send_photo(
                chat_id=message.chat.id,
                photo=config.START_IMG_URL,
                caption=_["start_2"].format(
                    message.from_user.mention, app.mention, UP, DISK, CPU, RAM
                ),
                reply_markup=InlineKeyboardMarkup(out),
                message_effect_id=get_random_effect_id()
            )
        except Exception:
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["start_2"].format(
                    message.from_user.mention, app.mention, UP, DISK, CPU, RAM
                ),
                reply_markup=InlineKeyboardMarkup(out)
            )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"{message.from_user.mention} just started the bot.\n"
                     f"User ID: <code>{message.from_user.id}</code>\n"
                     f"Username: @{message.from_user.username}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    # 🍓 Big animated reaction for groups  
    await send_animated_reaction(message, "🍓")

    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    try:
        await app.send_photo(
            chat_id=message.chat.id,
            photo=config.START_IMG_URL,
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
            message_effect_id=get_random_effect_id()
        )
    except Exception:
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out)
        )

    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await send_animated_reaction(message, "🍓")
                    try:
                        await app.send_message(chat_id=message.chat.id, text=_["start_4"])
                    except:
                        await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await send_animated_reaction(message, "🍓")
                    try:
                        await app.send_message(
                            chat_id=message.chat.id,
                            text=_["start_5"].format(
                                app.mention,
                                f"https://t.me/{app.username}?start=sudolist",
                                config.SUPPORT_GROUP,
                            ),
                            disable_web_page_preview=True
                        )
                    except:
                        await message.reply_text(
                            _["start_5"].format(
                                app.mention,
                                f"https://t.me/{app.username}?start=sudolist",
                                config.SUPPORT_GROUP,
                            ),
                            disable_web_page_preview=True,
                        )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await send_animated_reaction(message, "🍓")
                try:
                    await app.send_photo(
                        chat_id=message.chat.id,
                        photo=config.START_IMG_URL,
                        caption=_["start_3"].format(
                            message.from_user.first_name,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        reply_markup=InlineKeyboardMarkup(out),
                        message_effect_id=get_random_effect_id()
                    )
                except Exception:
                    await message.reply_photo(
                        photo=config.START_IMG_URL,
                        caption=_["start_3"].format(
                            message.from_user.first_name,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        reply_markup=InlineKeyboardMarkup(out),
                    )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(ex)


# Additional function for custom reactions with different effects
async def react_with_custom_effect(message: Message, emoji: str, effect_type: str = "fire"):
    """Send reaction with specific animation effect"""
    effect_map = {
        "fire": "5104841245755180586",
        "party": "5046509860389126442", 
        "thumbs": "5107584321108051014",
        "heart": "5159385139981059251",
        "love": "5159394597140101489"
    }
    
    effect_id = effect_map.get(effect_type, "5104841245755180586")
    
    try:
        # Try with premium effect
        await app.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=emoji,
            is_big=True
        )
        
        # Send additional message with effect if needed
        await asyncio.sleep(0.5)  # Small delay
        await app.send_message(
            chat_id=message.chat.id,
            text="🎉",
            reply_to_message_id=message.id,
            message_effect_id=int(effect_id)
        )
        
        # Delete the effect message after 2 seconds
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Custom effect reaction failed: {e}")
        # Fallback to normal reaction
        try:
            await message.react(emoji)
        except:
            pass
