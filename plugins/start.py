import os
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
URL = "https://streembot-009a426ab9b2.herokuapp.com/"  # Replace with your server URL
LOG_CHANNEL = -1002060163655  # Replace with your log channel ID

# Define bot
app = Client(
    "my_bot",
    api_id=int(os.environ.get("API_ID", 12345)),
    api_hash=os.environ.get("API_HASH", "your_api_hash"),
    bot_token=os.environ.get("BOT_TOKEN", "your_bot_token"),
)

@app.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    try:
        file = getattr(message, message.media.value)
        filename = file.file_name
        filesize = file.file_size
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        logger.info(f"File received - Name: {filename}, Size: {filesize}, User ID: {user_id}")

        # Generate stream link
        sanitized_filename = filename.replace(" ", "_").lower()
        stream_link = f"{URL}watch/{message.message_id}/{sanitized_filename}?hash={fileid}"

        # Prepare response
        msg_text = (
            f"<i><u>Your Link Generated!</u></i>\n\n"
            f"<b>File Name:</b> <i>{filename}</i>\n"
            f"<b>File Size:</b> <i>{filesize} bytes</i>\n"
            f"<b>Stream Link:</b> <i>{stream_link}</i>"
        )
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Generate Sample Video", callback_data="sample_video")],
            [InlineKeyboardButton("Generate Screenshot", callback_data="screenshot")],
            [InlineKeyboardButton("Extract Thumbnail", callback_data="thumbnail")]
        ])

        await message.reply_text(
            text=msg_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        # Log message to LOG_CHANNEL
        await client.send_message(
            LOG_CHANNEL,
            f"File received:\n\n"
            f"File Name: {filename}\n"
            f"File Size: {filesize} bytes\n"
            f"User: {username} (ID: {user_id})",
        )
    except Exception as e:
        logger.error(f"Error in stream_start: {e}")
        await message.reply_text("An error occurred while processing your file.")

@app.on_callback_query(filters.regex("thumbnail"))
async def extract_thumbnail(client, callback_query: CallbackQuery):
    try:
        logger.info("User selected Extract Thumbnail.")
        await callback_query.answer("Thumbnail extraction is not implemented yet.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in extract_thumbnail: {e}")

@app.on_callback_query(filters.regex("screenshot"))
async def generate_screenshot(client, callback_query: CallbackQuery):
    try:
        logger.info("User selected Generate Screenshot.")
        await callback_query.answer("Screenshot generation is not implemented yet.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in generate_screenshot: {e}")

@app.on_callback_query(filters.regex("sample_video"))
async def generate_sample_video(client, callback_query: CallbackQuery):
    try:
        logger.info("User selected Generate Sample Video.")
        await callback_query.answer("Sample video generation is not implemented yet.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in generate_sample_video: {e}")

if __name__ == "__main__":
    logger.info("Bot is starting...")
    app.run()
