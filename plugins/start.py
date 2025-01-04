import os
import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

# Ensure FFmpeg is installed on the server for this script to work.

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/JN2FLIX")]]
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )
    return


@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    fileid = file.file_id

    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
    file_name = quote_plus(get_name(log_msg))

    stream = f"{URL}watch/{str(log_msg.id)}/{file_name}?hash={get_hash(log_msg)}"
    download = f"{URL}{str(log_msg.id)}/{file_name}?hash={get_hash(log_msg)}"

    msg_text = f"""<i><u>Your Link Generated!</u></i>\n\n<b>📂 File Name:</b> <i>{get_name(log_msg)}</i>\n\n<b>📦 File Size:</b> <i>{filesize}</i>\n\n<b>📥 Download:</b> <i>{download}</i>\n\n<b>🖥 Watch:</b> <i>{stream}</i>\n\n<b>🚸 Note: Links won't expire until deleted</b>"""

    buttons = [
        [InlineKeyboardButton("🎥 Generate Sample Video", callback_data="generate_sample")],
        [InlineKeyboardButton("🖼 Generate Screenshot", callback_data="generate_screenshot")],
        [InlineKeyboardButton("📷 Extract Thumbnail", callback_data="extract_thumbnail")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await message.reply_text(
        text=msg_text,
        reply_markup=reply_markup,
        parse_mode="HTML",
        quote=True
    )


@Client.on_callback_query(filters.regex("generate_sample"))
async def generate_sample_video(client, callback_query: CallbackQuery):
    video_file_id = callback_query.message.video.file_id
    sample_file = "sample_video.mp4"
    duration = 30  # seconds

    cmd = [
        "ffmpeg",
        "-i", f"pipe:{video_file_id}",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        sample_file
    ]
    subprocess.run(cmd, stdin=subprocess.PIPE)

    await client.send_video(
        chat_id=callback_query.from_user.id,
        video=sample_file,
        caption="Here's your sample video!"
    )
    os.remove(sample_file)


@Client.on_callback_query(filters.regex("generate_screenshot"))
async def generate_screenshot(client, callback_query: CallbackQuery):
    video_file_id = callback_query.message.video.file_id
    screenshot_file = "screenshot.jpg"
    timestamp = random.randint(0, 60)  # Adjust max timestamp as needed

    cmd = [
        "ffmpeg",
        "-i", f"pipe:{video_file_id}",
        "-ss", str(timestamp),
        "-vframes", "1",
        screenshot_file
    ]
    subprocess.run(cmd, stdin=subprocess.PIPE)

    await client.send_photo(
        chat_id=callback_query.from_user.id,
        photo=screenshot_file,
        caption=f"Random screenshot from {timestamp} seconds!"
    )
    os.remove(screenshot_file)


@Client.on_callback_query(filters.regex("extract_thumbnail"))
async def extract_thumbnail(client, callback_query: CallbackQuery):
    video_file_id = callback_query.message.video.file_id
    thumbnail_file = "thumbnail.jpg"

    cmd = [
        "ffmpeg",
        "-i", f"pipe:{video_file_id}",
        "-vf", "thumbnail",
        "-frames:v", "1",
        thumbnail_file
    ]
    subprocess.run(cmd, stdin=subprocess.PIPE)

    await client.send_photo(
        chat_id=callback_query.from_user.id,
        photo=thumbnail_file,
        caption="Here's the extracted thumbnail!"
    )
    os.remove(thumbnail_file)
