import os
import subprocess
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from info import URL, LOG_CHANNEL, SHORTLINK
from pyrogram.errors import MessageNotModified


# Setup logging
logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = file.file_size
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    logging.info(f"File received and processing started.")
    logging.info(f"File details - Name: {filename}, Size: {filesize}, User ID: {user_id}")

    # Generate stream link (ensure you replace with the correct method)
    file_name = filename.replace(" ", "_").lower()  # Sanitizing filename
    stream_link = f"{URL}watch/{str(message.message_id)}/{file_name}?hash={fileid}"

    msg_text = f"<i><u>Your Link Generated!</u></i>\n\n<b>File Name:</b> <i>{filename}</i>\n\n<b>File Size:</b> <i>{filesize} bytes</i>\n\n<b>Stream Link:</b> <i>{stream_link}</i>"

    # Send reply with options
    options_buttons = [
        [InlineKeyboardButton("Generate Sample Video", callback_data="sample_video")],
        [InlineKeyboardButton("Generate Screenshot", callback_data="screenshot")],
        [InlineKeyboardButton("Extract Thumbnail", callback_data="thumbnail")]
    ]
    reply_markup = InlineKeyboardMarkup(options_buttons)

    await message.reply_text(
        text=msg_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


@Client.on_callback_query(filters.regex("thumbnail"))
async def extract_thumbnail(client, callback_query: CallbackQuery):
    try:
        # Ensure that the message contains a video
        if callback_query.message.video:
            logging.info("User selected Extract Thumbnail.")

            # Extract thumbnail using ffmpeg (You may need to download the video first)
            video_file = callback_query.message.video.file_id
            thumbnail_file = "thumbnail.jpg"
            cmd = [
                "ffmpeg", 
                "-i", video_file,
                "-vf", "thumbnail", 
                "-vframes", "1", 
                thumbnail_file
            ]
            subprocess.run(cmd, check=True)

            # Send the extracted thumbnail
            await client.send_photo(callback_query.from_user.id, photo=thumbnail_file)

            # Cleanup the thumbnail file
            os.remove(thumbnail_file)
            logging.info("Thumbnail extracted and sent.")
        else:
            # Handle the case where the message doesn't contain a video
            await callback_query.answer("Error: No video found to extract the thumbnail from.")
            logging.error("No video found in the message for thumbnail extraction.")
    
    except Exception as e:
        logging.error(f"Error extracting thumbnail: {e}")
        await callback_query.answer("Error while extracting the thumbnail.")


@Client.on_callback_query(filters.regex("screenshot"))
async def generate_screenshot(client, callback_query: CallbackQuery):
    try:
        # Ensure that the message contains a video
        if callback_query.message.video:
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
        else:
            # Handle the case where the message doesn't contain a video
            await callback_query.answer("Error: No video found to generate a screenshot from.")
            logging.error("No video found in the message for screenshot generation.")
    
    except Exception as e:
        logging.error(f"Error in generate_screenshot: {e}")
        await callback_query.answer("Error while generating the screenshot.")


@Client.on_callback_query(filters.regex(r"screenshot_(\d+)sec"))
async def take_screenshot(client, callback_query: CallbackQuery):
    try:
        # Ensure that the message contains a video
        if callback_query.message.video:
            time = callback_query.data.split("_")[1]
            logging.info(f"Taking screenshot at {time} seconds.")
            
            # Take screenshot using ffmpeg (You may need to download the video first)
            video_file = callback_query.message.video.file_id
            screenshot_file = f"screenshot_{time}.jpg"
            cmd = [
                "ffmpeg", 
                "-i", video_file,
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
        else:
            # Handle the case where the message doesn't contain a video
            await callback_query.answer("Error: No video found to generate a screenshot from.")
            logging.error("No video found in the message for screenshot generation.")
    
    except Exception as e:
        logging.error(f"Error taking screenshot: {e}")
        await callback_query.answer("Error while taking the screenshot.")


@Client.on_callback_query(filters.regex("sample_video"))
async def generate_sample_video(client, callback_query: CallbackQuery):
    try:
        # Ensure that the message contains a video
        if callback_query.message.video:
            logging.info("User selected Generate Sample Video.")
            
            # Ask for sample video options
            sample_video_buttons = [
                [InlineKeyboardButton("20 Seconds", callback_data="sample_video_20sec")],
                [InlineKeyboardButton("30 Seconds", callback_data="sample_video_30sec")],
                [InlineKeyboardButton("50 Seconds", callback_data="sample_video_50sec")]
            ]
            rm = InlineKeyboardMarkup(sample_video_buttons)
            await callback_query.message.edit_text(
                text="Select the duration for the sample video.",
                reply_markup=rm
            )
        else:
            # Handle the case where the message doesn't contain a video
            await callback_query.answer("Error: No video found to generate a sample video from.")
            logging.error("No video found in the message for sample video generation.")
    
    except Exception as e:
        logging.error(f"Error in generate_sample_video: {e}")
        await callback_query.answer("Error while generating the sample video.")


@Client.on_callback_query(filters.regex(r"sample_video_(\d+)sec"))
async def create_sample_video(client, callback_query: CallbackQuery):
    try:
        # Ensure that the message contains a video
        if callback_query.message.video:
            time = callback_query.data.split("_")[2]
            logging.info(f"Generating sample video of {time} seconds.")
            
            # Generate the sample video using ffmpeg (You may need to download the video first)
            video_file = callback_query.message.video.file_id
            sample_video_file = f"sample_{time}.mp4"
            cmd = [
                "ffmpeg", 
                "-i", video_file,
                "-t", time, 
                sample_video_file
            ]
            subprocess.run(cmd, check=True)
            
            # Send the sample video
            await client.send_video(callback_query.from_user.id, video=sample_video_file)

            # Log and cleanup
            os.remove(sample_video_file)
            logging.info(f"Sample video created and sent at {time} seconds.")
        else:
            # Handle the case where the message doesn't contain a video
            await callback_query.answer("Error: No video found to generate a sample video from.")
            logging.error("No video found in the message for sample video generation.")
    
    except Exception as e:
        logging.error(f"Error creating sample video: {e}")
        await callback_query.answer("Error while creating the sample video.")
