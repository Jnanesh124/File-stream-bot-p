import os
import random
import subprocess
import logging
import humanize  # <-- Add this import
import imageio_ffmpeg as ffmpeg  # <-- Added imageio_ffmpeg import
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
from info import URL, LOG_CHANNEL, SHORTLINK

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Function to check if FFmpeg is available
def check_ffmpeg():
    try:
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()  # Get the path to the ffmpeg binary
        logger.info(f"FFmpeg binary path: {ffmpeg_path}")
        subprocess.run([ffmpeg_path, '-version'], check=True)
        logger.info("FFmpeg is working!")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise Exception("FFmpeg not found or not working!")

# Check if FFmpeg is available at the start
check_ffmpeg()

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, f"New user joined: {message.from_user.id} - {message.from_user.mention}")
    
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/JN2FLIX")
        ]]
    )
    
    await client.send_message(
        chat_id=message.from_user.id,
        text=f"Hello {message.from_user.mention}, welcome to {temp.U_NAME}. Use this bot to generate links for your media.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )
    logger.info(f"Sent start message to {message.from_user.id}")

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    logger.info(f"Received media from {message.from_user.id}: {message.media}")
    
    try:
        # Check if the message contains file data
        file = getattr(message, message.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size)
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )

        # Get the thumbnail if available
        thumbnail_path = None
        if file.thumbs:
            thumbnail = file.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)
            logger.info(f"Thumbnail downloaded to {thumbnail_path}")

        # URL encode the filename
        fileName = quote_plus(get_name(log_msg))

        # Generate the stream and download links
        if SHORTLINK == False:
            stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
        else:
            stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")
            download = await get_shortlink(f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")

        # Prepare the message text
        msg_text = f"""<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{get_name(log_msg)}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{humanbytes(get_media_file_size(message))}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{download}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{stream}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

        # Add buttons for sample video, screenshot, and thumbnail
        rm = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("Generate Sample Video", callback_data="generate_sample_video"),
                InlineKeyboardButton("Generate Screenshot", callback_data="generate_screenshot"),
                InlineKeyboardButton("Generate Thumbnail", callback_data="generate_thumbnail")
            ]]
        )

        # Send the message with the thumbnail if available
        if thumbnail_path:
            try:
                await message.reply_photo(
                    photo=thumbnail_path,
                    caption=msg_text,
                    reply_markup=rm,
                    quote=True
                )
                logger.info(f"Sent thumbnail successfully to {message.from_user.id}")
            except Exception as e:
                logger.error(f"Error sending thumbnail: {e}")
        else:
            # If no thumbnail, just send the message with the links
            await message.reply_text(
                text=msg_text,
                reply_markup=rm,
                quote=True
            )
            logger.info(f"Sent file without thumbnail to {message.from_user.id}")

        # Clean up the thumbnail if it was downloaded
        if thumbnail_path:
            try:
                os.remove(thumbnail_path)
                logger.info(f"Deleted thumbnail: {thumbnail_path}")
            except Exception as e:
                logger.error(f"Error deleting thumbnail: {e}")

    except Exception as e:
        logger.error(f"Error in processing media: {e}")
        await message.reply_text(f"An error occurred while processing your file: {e}")


@Client.on_callback_query(filters.regex("generate_sample_video"))
async def generate_sample_video(client, callback_query):
    try:
        video_file_path = await client.download_media(callback_query.message)
        sample_file_path = f"/tmp/sample_{os.path.basename(video_file_path)}"

        # Generate sample video using ffmpeg
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        subprocess.run([ffmpeg_path, '-i', video_file_path, '-t', '00:00:30', '-c', 'copy', sample_file_path], check=True)

        # Send the generated sample video
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=sample_file_path,
            caption="Here is your sample video (30 seconds)."
        )

        # Clean up
        os.remove(video_file_path)
        os.remove(sample_file_path)
        logger.info("Sample video generated and sent successfully.")
    except Exception as e:
        logger.error(f"Error generating sample video: {e}")
        await callback_query.answer("Failed to generate sample video.")

@Client.on_callback_query(filters.regex("generate_screenshot"))
async def generate_screenshot(client, callback_query):
    try:
        video_file_path = await client.download_media(callback_query.message)
        screenshot_file_path = f"/tmp/screenshot_{os.path.basename(video_file_path)}.jpg"

        # Generate screenshot using ffmpeg (random frame)
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        subprocess.run([ffmpeg_path, '-i', video_file_path, '-vf', 'select=eq(n\,5)', '-vsync', 'vfr', screenshot_file_path], check=True)

        # Send the generated screenshot
        await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=screenshot_file_path,
            caption="Here is your screenshot."
        )

        # Clean up
        os.remove(video_file_path)
        os.remove(screenshot_file_path)
        logger.info("Screenshot generated and sent successfully.")
    except Exception as e:
        logger.error(f"Error generating screenshot: {e}")
        await callback_query.answer("Failed to generate screenshot.")

@Client.on_callback_query(filters.regex("generate_thumbnail"))
async def generate_thumbnail(client, callback_query):
    try:
        video_file_path = await client.download_media(callback_query.message)
        thumbnail_file_path = f"/tmp/thumbnail_{os.path.basename(video_file_path)}.jpg"

        # Generate thumbnail using ffmpeg
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        subprocess.run([ffmpeg_path, '-i', video_file_path, '-vf', 'thumbnail', '-vframes', '1', thumbnail_file_path], check=True)

        # Send the generated thumbnail
        await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=thumbnail_file_path,
            caption="Here is your video thumbnail."
        )

        # Clean up
        os.remove(video_file_path)
        os.remove(thumbnail_file_path)
        logger.info("Thumbnail generated and sent successfully.")
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        await callback_query.answer("Failed to generate thumbnail.")
