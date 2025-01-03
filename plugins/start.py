import os
import humanize
import hashlib
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from urllib.parse import quote_plus
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
from info import URL, LOG_CHANNEL, SHORTLINK

# Define get_hash function
def get_hash(log_msg_id, filename):
    """
    Generate a consistent hash using both the log_msg_id and filename.
    This ensures the hash is unique and can be validated correctly.
    """
    # Ensure the filename is URL-encoded before generating the hash
    filename_encoded = quote_plus(filename)
    return hashlib.md5(f"{log_msg_id}{filename_encoded}".encode()).hexdigest()

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    try:
        # Get file details
        file = getattr(message, message.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size)
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        # Send the "Please wait, generating links..." message
        wait_msg = await client.send_message(
            chat_id=user_id,
            text="Please wait, generating links...",
        )

        # Initialize variables for thumbnail and download
        thumbnail_path = None
        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )

        # Check for the thumbnail
        if file.thumbs:
            thumbnail = file.thumbs[0].file_id
            thumbnail_path = await client.download_media(thumbnail)
            print(f"Thumbnail downloaded to {thumbnail_path}")  # Debugging log

        # URL encode the filename to handle special characters
        fileName = quote_plus(filename)  # URL encode the filename

        # Generate hash for the URL based on the log_msg_id and filename
        hash_value = get_hash(log_msg.id, filename)

        # Generate the URLs
        if not SHORTLINK:
            stream = f"{URL}watch/{log_msg.id}/{fileName}?hash={hash_value}"
            download = f"{URL}{log_msg.id}/{fileName}?hash={hash_value}"
        else:
            stream = await get_shortlink(f"{URL}watch/{log_msg.id}/{fileName}?hash={hash_value}")
            download = await get_shortlink(f"{URL}{log_msg.id}/{fileName}?hash={hash_value}")

        # Send the response with the thumbnail and links
        if thumbnail_path:
            await client.send_photo(
                chat_id=user_id,
                photo=thumbnail_path,
                caption=f"""<strong>📂 Fɪʟᴇ ɴᴀᴍᴇ :</strong> <b>{filename}</b>
                        \n\n<strong>📦 Fɪʟᴇ ꜱɪᴢᴇ :</strong> <b>{filesize}</b>
                        \n\n<strong>🚀 Download Link:</strong> {download}
                        \n\n<strong>🖥️ Watch Online Link:</strong> {stream}""",
                parse_mode=enums.ParseMode.HTML
            )
            print(f"Sent file with thumbnail: {thumbnail_path}")  # Debugging log
        else:
            await client.send_message(
                chat_id=user_id,
                text=f"""<strong>📂 Fɪʟᴇ ɴᴀᴍᴇ :</strong> <b>{filename}</b>
                        \n\n<strong>📦 Fɪʟᴇ ꜱɪᴢᴇ :</strong> <b>{filesize}</b>
                        \n\n<strong>🚀 Download Link:</strong> {download}
                        \n\n<strong>🖥️ Watch Online Link:</strong> {stream}""",
                parse_mode=enums.ParseMode.HTML
            )
            print(f"Sent file without thumbnail")  # Debugging log

        # Delete the "Please wait" message
        await wait_msg.delete()
        print("Deleted 'Please wait' message")  # Debugging log

        # Clean up the thumbnail if it was downloaded
        if thumbnail_path:
            os.remove(thumbnail_path)
            print(f"Deleted thumbnail: {thumbnail_path}")  # Debugging log

    except Exception as e:
        print(f"Error processing message: {e}")
