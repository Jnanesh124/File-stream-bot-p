import os
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
import humanize
from info import URL, LOG_CHANNEL, SHORTLINK, AUTH_CHANNEL, SECOND_AUTH_CHANNEL  # Import numeric channel IDs
from pyrogram.errors import UserNotParticipant  # Import this

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

# Function to check subscription status
async def is_subscribed(bot, user_id, channels):
    btn = []
    
    # Log the channels being checked
    logger.debug(f"Checking subscription for channels: {channels}")
    
    for id in channels:
        try:
            # Ensure the channel ID is numeric (not a username)
            if not isinstance(id, int):
                raise ValueError(f"Channel ID should be an integer. Got: {type(id)}")

            await bot.get_chat_member(id, user_id)
        except UserNotParticipant:
            chat = await bot.get_chat(id)
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            logger.error(f"Error in subscription check for channel {id}: {e}")
            btn.append([InlineKeyboardButton(f"Error: {e}", url="https://t.me/" + str(id))])
    return btn

# Handle the /start command
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, f"New user joined: {message.from_user.id} - {message.from_user.mention}")

    # Check for subscription to both channels
    btn = await is_subscribed(client, message.from_user.id, [AUTH_CHANNEL, SECOND_AUTH_CHANNEL])
    if btn:
        username = (await client.get_me()).username
        btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
        await message.reply_text(
            text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the required channels first, then click on Try Again. 😇</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return  # Stop further processing if the user is not subscribed

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

# Handle file uploads
@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    logger.info(f"Received media from {message.from_user.id}: {message.media}")
    
    try:
        # Check subscription status for both channels
        btn = await is_subscribed(client, message.from_user.id, [AUTH_CHANNEL, SECOND_AUTH_CHANNEL])
        if btn:
            username = (await client.get_me()).username
            btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
            await message.reply_text(
                text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the required channels first, then click on Try Again. 😇</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return  # Stop further processing if the user is not subscribed
        
        if not hasattr(message, message.media.value):
            logger.error(f"No media found in the message from {message.from_user.id}")
            await message.reply_text("No media found in your message.")
            return
        
        file = getattr(message, message.media.value)
        filename = file.file_name if hasattr(file, 'file_name') else "unknown_file"
        filesize = humanize.naturalsize(file.file_size)
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )

        thumbnail_path = None
        if file.thumbs:
            thumbnail = file.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)
            logger.info(f"Thumbnail downloaded to {thumbnail_path}")

        fileName = quote_plus(str(get_name(log_msg)) if get_name(log_msg) else "default_file_name")

        if SHORTLINK == False:
            stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
        else:
            stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")
            download = await get_shortlink(f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")

        msg_text = (f"<i><u>Your Link Generated!</u></i>\n\n"
                    f"<b>📂 File Name:</b> <i>{get_name(log_msg)}</i>\n\n"
                    f"<b>📦 File Size:</b> <i>{filesize}</i>\n\n"
                    f"<b>🔗 Stream:</b> <i><a href='{stream}'>Watch</a></i>\n\n"
                    f"<b>⬇️ Download:</b> <i><a href='{download}'>Download</a></i>")

        if thumbnail_path:
            try:
                await message.reply_photo(
                    photo=thumbnail_path,
                    caption=msg_text,
                    quote=True
                )
                logger.info(f"Sent thumbnail successfully to {message.from_user.id}")
            except Exception as e:
                logger.error(f"Error sending thumbnail: {e}")
                await message.reply_text(f"Error sending thumbnail: {e}")
        else:
            await message.reply_text(
                text=msg_text,
                quote=True
            )
            logger.info(f"Sent file without thumbnail to {message.from_user.id}")

        if thumbnail_path:
            try:
                os.remove(thumbnail_path)
                logger.info(f"Deleted thumbnail: {thumbnail_path}")
            except Exception as e:
                logger.error(f"Error deleting thumbnail: {e}")

    except Exception as e:
        logger.error(f"Error processing media from user {message.from_user.id}: {e}")
        await message.reply_text(f"An error occurred while processing your file: {e}")
