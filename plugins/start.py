import os
import random
import humanize
import logging
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

        # Send the message with the thumbnail if available
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
        else:
            # If no thumbnail, just send the message with the links
            await message.reply_text(
                text=msg_text,
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

