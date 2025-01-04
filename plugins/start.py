import os
import random
import subprocess
import tempfile
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from urllib.parse import quote_plus
from info import URL, LOG_CHANNEL
from TechVJ.util.file_properties import get_name, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/JN2FLIX")]]
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=f"Hello {message.from_user.mention}, welcome to {temp.U_NAME}!",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanbytes(file.file_size)
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )

    # Generate Stream and Download Links
    fileName = quote_plus(get_name(log_msg))
    stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
    download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"

    # Prepare Buttons for User to Choose
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Generate Sample Video", callback_data="generate_sample"),
            InlineKeyboardButton("Generate Screenshot", callback_data="generate_screenshot"),
            InlineKeyboardButton("Generate Thumbnail", callback_data="generate_thumbnail"),
        ]
    ])

    # Send message with options
    await client.send_message(
        chat_id=message.from_user.id,
        text=f"File Name: {filename}\nFile Size: {filesize}",
        reply_markup=markup,
    )

@Client.on_callback_query(filters.regex("generate_sample"))
async def generate_sample(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Reply with options for sample video duration
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("20 sec", callback_data="sample_20sec"),
            InlineKeyboardButton("30 sec", callback_data="sample_30sec"),
            InlineKeyboardButton("50 sec", callback_data="sample_50sec"),
        ]
    ])
    await callback_query.answer("Choose sample video duration:", show_alert=False)
    await callback_query.message.edit_reply_markup(markup)

@Client.on_callback_query(filters.regex("sample_20sec|sample_30sec|sample_50sec"))
async def process_sample(client, callback_query: CallbackQuery):
    duration = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    # Get the file stream link (you'll get this from earlier messages)
    file_url = "your_stream_url_here"

    # Generate sample video using ffmpeg
    output_file = tempfile.mktemp(suffix=".mp4")
    try:
        command = [
            "ffmpeg", "-i", file_url, "-t", duration, "-c:v", "libx264", "-c:a", "aac", output_file
        ]
        subprocess.run(command, check=True)

        # Send the generated sample video
        await client.send_video(
            chat_id=user_id,
            video=output_file,
            caption=f"Sample video of {duration} seconds."
        )
        os.remove(output_file)  # Clean up the temporary file
    except Exception as e:
        print(f"Error generating sample video: {e}")
        await callback_query.message.edit("An error occurred while generating the sample video.")

@Client.on_callback_query(filters.regex("generate_screenshot"))
async def generate_screenshot(client, callback_query: CallbackQuery):
    # Reply with options for screenshot time
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("3 sec", callback_data="screenshot_3sec"),
            InlineKeyboardButton("5 sec", callback_data="screenshot_5sec"),
            InlineKeyboardButton("7 sec", callback_data="screenshot_7sec"),
            InlineKeyboardButton("10 sec", callback_data="screenshot_10sec"),
        ]
    ])
    await callback_query.answer("Choose a time for the screenshot:", show_alert=False)
    await callback_query.message.edit_reply_markup(markup)

@Client.on_callback_query(filters.regex("screenshot_3sec|screenshot_5sec|screenshot_7sec|screenshot_10sec"))
async def process_screenshot(client, callback_query: CallbackQuery):
    time = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    # Get the file stream link
    file_url = "your_stream_url_here"

    # Generate screenshot using ffmpeg
    output_file = tempfile.mktemp(suffix=".jpg")
    try:
        command = [
            "ffmpeg", "-i", file_url, "-ss", time, "-vframes", "1", output_file
        ]
        subprocess.run(command, check=True)

        # Send the generated screenshot
        await client.send_photo(
            chat_id=user_id,
            photo=output_file,
            caption=f"Screenshot at {time} seconds."
        )
        os.remove(output_file)  # Clean up the temporary file
    except Exception as e:
        print(f"Error generating screenshot: {e}")
        await callback_query.message.edit("An error occurred while generating the screenshot.")

@Client.on_callback_query(filters.regex("generate_thumbnail"))
async def generate_thumbnail(client, callback_query: CallbackQuery):
    # Get the file stream link
    file_url = "your_stream_url_here"

    # Generate thumbnail using ffmpeg
    output_file = tempfile.mktemp(suffix=".jpg")
    try:
        command = [
            "ffmpeg", "-i", file_url, "-vframes", "1", output_file
        ]
        subprocess.run(command, check=True)

        # Send the generated thumbnail
        await client.send_photo(
            chat_id=callback_query.from_user.id,
            photo=output_file,
            caption="Generated Thumbnail."
        )
        os.remove(output_file)  # Clean up the temporary file
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        await callback_query.message.edit("An error occurred while generating the thumbnail.")
