import os
import random
import subprocess
import logging
import humanize
import imageio_ffmpeg as ffmpeg
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
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
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
        msg_text = (f"<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n"
                    f"<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{get_name(log_msg)}</i>\n\n"
                    f"<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{filesize}</i>\n\n"
                    f"<b>🔗 Stream :</b> <i><a href='{stream}'>Watch</a></i>\n\n"
                    f"<b>⬇️ Download :</b> <i><a href='{download}'>Download</a></i>")

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
        sample_file_path = f"/tmp/sample_{os.path.basename(video_file_path).split('.')[0]}.mp4"

        # Generate sample video using ffmpeg with explicit parameters for video and audio quality
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()

        # Set the output video to 20 seconds, with a constant frame rate and specific bitrate
        subprocess.run([
            ffmpeg_path,
            '-i', video_file_path,
            '-t', '00:00:20',            # Set the duration to 20 seconds
            '-c:v', 'libx264',           # Use the x264 codec for video
            '-c:a', 'aac',               # Use AAC codec for audio
            '-b:v', '1000k',             # Set video bitrate to 1000kbps (adjust if necessary)
            '-r', '30',                  # Set the frame rate to 30 fps
            '-s', '640x360',             # Optional: Set the resolution to 640x360 (adjust as needed)
            '-strict', 'experimental',
            sample_file_path
        ], check=True)

        # Send the generated sample video (ensure it's sent as a video file)
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=sample_file_path,
            caption="Here is your sample video (20 seconds)."
        )

        # Clean up
        os.remove(video_file_path)  # Remove the original video file
        os.remove(sample_file_path)  # Remove the generated sample video
        logger.info("Sample video generated and sent successfully.")
    except Exception as e:
        logger.error(f"Error generating sample video: {e}")
        await callback_query.answer("Failed to generate sample video.")
        
@Client.on_callback_query(filters.regex("generate_screenshot"))
async def generate_screenshot(client, callback_query):
    try:
        video_file_path = await client.download_media(callback_query.message)
        screenshot_file_paths = [f"/tmp/screenshot_{i}_{os.path.basename(video_file_path)}.jpg" for i in range(1, 6)]

        # Generate screenshots at 5 random timestamps
        duration = subprocess.check_output(
            [ffmpeg.get_ffmpeg_exe(), '-i', video_file_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']
        ).decode().strip()
        duration = float(duration)
        timestamps = sorted(random.sample(range(1, int(duration)), 5))

        for t, screenshot_file_path in zip(timestamps, screenshot_file_paths):
            subprocess.run([ffmpeg.get_ffmpeg_exe(), '-i', video_file_path, '-vf', f'select=gte(n\\,{t})', '-vframes', '1', '-vsync', 'vfr', screenshot_file_path], check=True)

        # Send the generated screenshots
        for screenshot_file_path in screenshot_file_paths:
            await client.send_photo(
                chat_id=callback_query.message.chat.id,
                photo=screenshot_file_path,
                caption="Here is your screenshot."
            )

        # Clean up
        os.remove(video_file_path)
        for screenshot_file_path in screenshot_file_paths:
            os.remove(screenshot_file_path)
        logger.info("Screenshots generated and sent successfully.")
    except Exception as e:
        logger.error(f"Error generating screenshots: {e}")
        await callback_query.answer("Failed to generate screenshots.")

@Client.on_callback_query(filters.regex("generate_thumbnail"))
async def generate_thumbnail(client, callback_query):
    try:
        video_file_path = await client.download_media(callback_query.message)
        thumbnail_file_path = f"/tmp/thumbnail_{os.path.basename(video_file_path)}.jpg"

        # Generate thumbnail using ffmpeg
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        subprocess.run([ffmpeg_path, '-i', video_file_path, '-vframes', '1', '-an', '-s', '320x240', '-f', 'image2', thumbnail_file_path], check=True)

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
