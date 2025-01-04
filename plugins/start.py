import os
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

# Initialize your bot with the proper API credentials
app = Client("my_bot")  # Make sure to replace "my_bot" with your actual session name

@app.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, f"New user started the bot: {message.from_user.mention}")

    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/JN2FLIX")
        ]]
    )

    await client.send_message(
        chat_id=message.from_user.id,
        text=f"Hello {message.from_user.mention}, welcome to the service!",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    fileid = file.file_id
    user_id = message.from_user.id

    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)

    # Handle thumbnail downloading if available
    thumbnail_path = None
    if file.thumbs:
        thumbnail = file.thumbs[0].file_id
        thumbnail_path = await client.download_media(thumbnail)

    # URL encode the filename
    fileName = quote_plus(get_name(log_msg))
    stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
    download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"

    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱!</u></i>\n\n<b>📂 File name :</b> <i>{}</i>\n\n<b>📦 File size :</b> <i>{}</i>\n\n<b>📥 Download :</b> <i>{}</i>\n\n<b>🖥 Watch :</b> <i>{}</i>"""

    # Send buttons for additional user actions
    action_buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🎞 Generate Sample Video", callback_data="generate_sample"),
            InlineKeyboardButton("📷 Generate Screenshot", callback_data="generate_screenshot"),
            InlineKeyboardButton("🌄 Extract Thumbnail", callback_data="extract_thumbnail"),
        ]]
    )

    await message.reply_text(
        text="<i>What would you like to do?</i>",
        reply_markup=action_buttons,
        quote=True
    )

    # Send the message with the file information
    if thumbnail_path:
        await message.reply_photo(
            photo=thumbnail_path,
            caption=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
            quote=True
        )
    else:
        await message.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
            quote=True
        )

    # Clean up the thumbnail if it was downloaded
    if thumbnail_path:
        try:
            os.remove(thumbnail_path)
        except Exception as e:
            print(f"Error deleting thumbnail: {e}")

@app.on_callback_query()
async def handle_query(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    await callback_query.answer()  # Acknowledge the callback query

    if callback_query.data == "generate_sample":
        await callback_query.message.reply_text("Generating sample video... (this feature is not yet implemented)")
        return

    elif callback_query.data == "generate_screenshot":
        await callback_query.message.reply_text("Generating screenshot... (this feature is not yet implemented)")
        return

    elif callback_query.data == "extract_thumbnail":
        await callback_query.message.reply_text("Extracting thumbnail... (this feature is not yet implemented)")
        return

    await callback_query.message.delete()

# Placeholder functions (implement these as needed)
async def generate_sample_video(file_id):
    print("Sample video generation triggered for file ID:", file_id)

async def generate_screenshot(file_id):
    print("Screenshot generation triggered for file ID:", file_id)

async def extract_thumbnail(file_id):
    print("Thumbnail extraction triggered for file ID:", file_id)
