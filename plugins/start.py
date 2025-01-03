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
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/vj_botz")
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
    user_id = message.from_user.id
    username =  message.from_user.mention 

    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )
    
    # Get the thumbnail if available
    thumbnail_path = None
    if file.thumbs:
        thumbnail = file.thumbs[0].file_id
        thumbnail_path = await client.download_media(thumbnail)
        print(f"Thumbnail downloaded to {thumbnail_path}")  # Debugging log
    
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
    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

    # Send the message with the thumbnail if available
    if thumbnail_path:
        print(f"Sending thumbnail: {thumbnail_path}")  # Debugging log
        try:
            await message.reply_photo(
                photo=thumbnail_path,
                caption=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
                quote=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                         InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)]
                    ]
                )
            )
            print(f"Thumbnail sent successfully: {thumbnail_path}")  # Debugging log
        except Exception as e:
            print(f"Error sending thumbnail: {e}")  # Error log
    else:
        # If no thumbnail, just send the message with the links
        await message.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
            quote=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                     InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)]
                ]
            )
        )
        print("Sent file without thumbnail")  # Debugging log

    # Clean up the thumbnail if it was downloaded
    if thumbnail_path:
        try:
            os.remove(thumbnail_path)
            print(f"Deleted thumbnail: {thumbnail_path}")  # Debugging log
        except Exception as e:
            print(f"Error deleting thumbnail: {e}")  # Error log
