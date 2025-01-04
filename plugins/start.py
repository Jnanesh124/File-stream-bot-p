import os
import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
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
    fileid = file.file_id
    user_id = message.from_user.id

    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )

    fileName = quote_plus(get_name(log_msg))
    stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"

    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Generate Sample Video", callback_data=f"sample_{log_msg.id}_{stream}"),
            InlineKeyboardButton("Generate Screenshot", callback_data=f"screenshot_{log_msg.id}_{stream}"),
            InlineKeyboardButton("Extract Thumbnail", callback_data=f"thumbnail_{log_msg.id}_{stream}")
        ]]
    )

    await message.reply_text(
        text="Choose an option below:",
        reply_markup=buttons,
        quote=True
    )
    print(f"Stream link generated for file: {get_name(log_msg)}")  # Log


@Client.on_callback_query(filters.regex(r"^sample_(\d+)_(.+)"))
async def generate_sample(client, callback_query):
    _, log_id, stream_link = callback_query.data.split("_", 2)

    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("20 Sec", callback_data=f"sample_time_{log_id}_{stream_link}_20"),
            InlineKeyboardButton("30 Sec", callback_data=f"sample_time_{log_id}_{stream_link}_30"),
            InlineKeyboardButton("50 Sec", callback_data=f"sample_time_{log_id}_{stream_link}_50")
        ]]
    )

    await callback_query.message.edit_text("Choose sample duration:", reply_markup=buttons)
    print("User selected Generate Sample Video.")  # Log


@Client.on_callback_query(filters.regex(r"^sample_time_(\d+)_(.+)_(\d+)"))
async def process_sample(client, callback_query):
    _, log_id, stream_link, duration = callback_query.data.split("_", 3)
    await callback_query.message.edit_text(f"Generating a {duration}-second sample video. This may take some time...")
    print(f"Generating {duration}-second sample video for stream: {stream_link}")  # Log


@Client.on_callback_query(filters.regex(r"^screenshot_(\d+)_(.+)"))
async def generate_screenshot(client, callback_query):
    _, log_id, stream_link = callback_query.data.split("_", 2)

    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("3 Screenshots", callback_data=f"screenshot_count_{log_id}_{stream_link}_3"),
            InlineKeyboardButton("5 Screenshots", callback_data=f"screenshot_count_{log_id}_{stream_link}_5"),
            InlineKeyboardButton("7 Screenshots", callback_data=f"screenshot_count_{log_id}_{stream_link}_7"),
            InlineKeyboardButton("10 Screenshots", callback_data=f"screenshot_count_{log_id}_{stream_link}_10")
        ]]
    )

    await callback_query.message.edit_text("Choose the number of screenshots:", reply_markup=buttons)
    print("User selected Generate Screenshot.")  # Log


@Client.on_callback_query(filters.regex(r"^screenshot_count_(\d+)_(.+)_(\d+)"))
async def process_screenshot(client, callback_query):
    _, log_id, stream_link, count = callback_query.data.split("_", 3)
    await callback_query.message.edit_text(f"Generating {count} screenshots. This may take some time...")
    print(f"Generating {count} screenshots for stream: {stream_link}")  # Log


@Client.on_callback_query(filters.regex(r"^thumbnail_(\d+)_(.+)"))
async def extract_thumbnail(client, callback_query):
    _, log_id, stream_link = callback_query.data.split("_", 2)
    await callback_query.message.edit_text("Extracting thumbnail. This may take some time...")
    print(f"Extracting thumbnail for stream: {stream_link}")  # Log
