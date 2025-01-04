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


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/JN2FLIX")
        ]]
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
    fileName = quote_plus(get_name(log_msg))
    stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"

    buttons = [
        [InlineKeyboardButton("🎥 Sample Video", callback_data=f"sample_{log_msg.id}")],
        [InlineKeyboardButton("📸 Screenshot", callback_data=f"screenshot_{log_msg.id}")],
        [InlineKeyboardButton("🖼️ Extract Thumbnail", callback_data=f"thumbnail_{log_msg.id}")]
    ]

    await message.reply_text(
        text=f"<b>File:</b> {filename}\n<b>Size:</b> {filesize}\n<b>Stream Link:</b> {stream}",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )


@Client.on_callback_query(filters.regex(r"sample_(\d+)"))
async def generate_sample_video(client, callback_query: CallbackQuery):
    message_id = int(callback_query.data.split("_")[1])
    file_path = await client.download_media(callback_query.message.reply_to_message.video.file_id, file_name=f"sample_{message_id}.mp4", progress=None)

    output_file = f"sample_video_{message_id}.mp4"
    os.system(f"ffmpeg -i {file_path} -ss 00:00:10 -t 00:00:20 -c copy {output_file}")

    await client.send_video(
        chat_id=callback_query.message.chat.id,
        video=output_file,
        caption="Sample Video Generated!"
    )
    os.remove(output_file)


@Client.on_callback_query(filters.regex(r"screenshot_(\d+)"))
async def generate_screenshot(client, callback_query: CallbackQuery):
    message_id = int(callback_query.data.split("_")[1])
    file_path = await client.download_media(callback_query.message.reply_to_message.video.file_id, file_name=f"video_{message_id}.mp4", progress=None)

    output_image = f"screenshot_{message_id}.jpg"
    os.system(f"ffmpeg -i {file_path} -vf thumbnail -frames:v 1 {output_image}")

    await client.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=output_image,
        caption="Screenshot Generated!"
    )
    os.remove(output_image)


@Client.on_callback_query(filters.regex(r"thumbnail_(\d+)"))
async def extract_thumbnail(client, callback_query: CallbackQuery):
    file = callback_query.message.reply_to_message.video
    if file.thumbs:
        thumb = file.thumbs[0].file_id
        thumbnail_path = await client.download_media(thumb)

        await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=thumbnail_path,
            caption="Thumbnail Extracted!"
        )
        os.remove(thumbnail_path)
    else:
        await callback_query.answer("No thumbnail available for this file!", show_alert=True)
