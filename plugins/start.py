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
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

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
    try:
        file = getattr(message, message.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size)
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        # Logging file details
        logging.info(f"File received and processing started.")
        logging.info(f"File details - Name: {filename}, Size: {filesize}, User ID: {user_id}")
        
        # Send log to the log channel
        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )

        # URL encode the filename
        fileName = quote_plus(get_name(log_msg))

        # Generate the stream and download links
        if SHORTLINK == False:
            stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
        else:
            stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")
            download = await get_shortlink(f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")

        msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

        # Send the message with the options
        buttons = [
            [InlineKeyboardButton("🎥 Generate Sample Video", callback_data="sample_video")],
            [InlineKeyboardButton("📸 Generate Screenshot", callback_data="screenshot")],
            [InlineKeyboardButton("📷 Extract Thumbnail", callback_data="thumbnail")]
        ]
        rm = InlineKeyboardMarkup(buttons)

        await client.send_message(
            chat_id=message.from_user.id,
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )

        # Log the action
        logging.info("Sending message with options...")

    except Exception as e:
        logging.error(f"Error in stream_start: {e}")
        await client.send_message(message.from_user.id, "Sorry, something went wrong. Please try again later.")


@Client.on_callback_query(filters.regex("sample_video"))
async def process_sample_video(client, callback_query: CallbackQuery):
    try:
        logging.info("User selected Generate Sample Video.")
        # Ask for the duration options
        duration_buttons = [
            [InlineKeyboardButton("20 Seconds", callback_data="sample_video_20sec")],
            [InlineKeyboardButton("30 Seconds", callback_data="sample_video_30sec")],
            [InlineKeyboardButton("50 Seconds", callback_data="sample_video_50sec")]
        ]
        rm = InlineKeyboardMarkup(duration_buttons)
        await callback_query.message.edit_text(
            text="Select the duration for the sample video.",
            reply_markup=rm
        )
    except Exception as e:
        logging.error(f"Error in process_sample_video: {e}")
        await callback_query.answer("Error while processing the sample video.")


@Client.on_callback_query(filters.regex(r"sample_video_(\d+)sec"))
async def generate_sample_video(client, callback_query: CallbackQuery):
    try:
        duration = callback_query.data.split("_")[2]
        logging.info(f"Generating sample video of {duration} seconds.")
        
        # Generate the sample video using ffmpeg
        video_file = callback_query.message.reply_to_message
        output_file = f"sample_{duration}.mp4"
        cmd = [
            "ffmpeg", 
            "-i", video_file.video.file_id, 
            "-t", duration, 
            "-c:v", "libx264", 
            "-c:a", "aac", 
            output_file
        ]
        subprocess.run(cmd, check=True)
        
        # Send the generated video
        await client.send_video(callback_query.from_user.id, video=output_file)

        # Log and cleanup
        os.remove(output_file)
        logging.info(f"Sample video generated and sent. Duration: {duration} seconds.")
    
    except Exception as e:
        logging.error(f"Error generating sample video: {e}")
        await callback_query.answer("Error while generating the sample video.")


@Client.on_callback_query(filters.regex("screenshot"))
async def generate_screenshot(client, callback_query: CallbackQuery):
    try:
        logging.info("User selected Generate Screenshot.")
        
        # Ask for screenshot options
        screenshot_buttons = [
            [InlineKeyboardButton("5 Seconds", callback_data="screenshot_5sec")],
            [InlineKeyboardButton("10 Seconds", callback_data="screenshot_10sec")]
        ]
        rm = InlineKeyboardMarkup(screenshot_buttons)
        await callback_query.message.edit_text(
            text="Select the time for the screenshot.",
            reply_markup=rm
        )
    except Exception as e:
        logging.error(f"Error in generate_screenshot: {e}")
        await callback_query.answer("Error while generating the screenshot.")


@Client.on_callback_query(filters.regex(r"screenshot_(\d+)sec"))
async def take_screenshot(client, callback_query: CallbackQuery):
    try:
        time = callback_query.data.split("_")[1]
        logging.info(f"Taking screenshot at {time} seconds.")
        
        # Take screenshot using ffmpeg
        video_file = callback_query.message.reply_to_message
        screenshot_file = f"screenshot_{time}.jpg"
        cmd = [
            "ffmpeg", 
            "-i", video_file.video.file_id,
            "-ss", time, 
            "-vframes", "1", 
            screenshot_file
        ]
        subprocess.run(cmd, check=True)
        
        # Send the screenshot
        await client.send_photo(callback_query.from_user.id, photo=screenshot_file)

        # Log and cleanup
        os.remove(screenshot_file)
        logging.info(f"Screenshot taken and sent at {time} seconds.")
    
    except Exception as e:
        logging.error(f"Error taking screenshot: {e}")
        await callback_query.answer("Error while taking the screenshot.")


@Client.on_callback_query(filters.regex("thumbnail"))
async def extract_thumbnail(client, callback_query: CallbackQuery):
    try:
        logging.info("User selected Extract Thumbnail.")
        
        # Extract thumbnail
        video_file = callback_query.message.reply_to_message
        thumbnail_file = f"thumbnail.jpg"
        cmd = [
            "ffmpeg", 
            "-i", video_file.video.file_id,
            "-vf", "thumbnail", 
            "-vframes", "1", 
            thumbnail_file
        ]
        subprocess.run(cmd, check=True)
        
        # Send the thumbnail
        await client.send_photo(callback_query.from_user.id, photo=thumbnail_file)

        # Log and cleanup
        os.remove(thumbnail_file)
        logging.info("Thumbnail extracted and sent.")
    
    except Exception as e:
        logging.error(f"Error extracting thumbnail: {e}")
        await callback_query.answer("Error while extracting the thumbnail.")
