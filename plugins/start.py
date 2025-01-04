import os
import subprocess
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from info import URL, LOG_CHANNEL

# Setup logging
logging.basicConfig(level=logging.INFO)


async def download_partial_video(client, file_id, duration, output_file):
    """
    Downloads a small portion of the video using ffmpeg.
    Args:
        client: Pyrogram client.
        file_id: The file ID of the video from Telegram.
        duration: Duration (in seconds) to download.
        output_file: Name of the output file.
    Returns:
        Path to the downloaded file.
    """
    logging.info(f"Starting partial download: {duration} seconds.")
    input_file = await client.download_media(file_id, file_name="input_file")
    
    # Use ffmpeg to trim the required portion
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-t", str(duration),
        "-c", "copy",
        output_file
    ]
    subprocess.run(cmd, check=True)
    os.remove(input_file)  # Clean up input file
    return output_file


@Client.on_callback_query(filters.regex("thumbnail"))
async def extract_thumbnail(client, callback_query: CallbackQuery):
    try:
        if callback_query.message.video:
            logging.info("User selected Extract Thumbnail.")
            
            # Download only the first few seconds
            partial_video = await download_partial_video(
                client,
                callback_query.message.video.file_id,
                duration=5,
                output_file="partial_video.mp4"
            )
            thumbnail_file = "thumbnail.jpg"

            # Generate thumbnail using ffmpeg
            cmd = [
                "ffmpeg",
                "-i", partial_video,
                "-vf", "thumbnail",
                "-vframes", "1",
                thumbnail_file
            ]
            subprocess.run(cmd, check=True)

            await client.send_photo(callback_query.from_user.id, photo=thumbnail_file)

            # Clean up
            os.remove(thumbnail_file)
            os.remove(partial_video)
            logging.info("Thumbnail extracted and sent.")
        else:
            await callback_query.answer("Error: No video found to extract the thumbnail from.")
            logging.error("No video found in the message for thumbnail extraction.")
    
    except Exception as e:
        logging.error(f"Error extracting thumbnail: {e}")
        await callback_query.answer("Error while extracting the thumbnail.")


@Client.on_callback_query(filters.regex(r"screenshot_(\d+)sec"))
async def take_screenshot(client, callback_query: CallbackQuery):
    try:
        if callback_query.message.video:
            time = callback_query.data.split("_")[1]
            logging.info(f"Taking screenshot at {time} seconds.")

            # Download a small portion of the video around the desired timestamp
            partial_video = await download_partial_video(
                client,
                callback_query.message.video.file_id,
                duration=int(time) + 1,  # Ensure we cover the required timestamp
                output_file="partial_video.mp4"
            )
            screenshot_file = f"screenshot_{time}.jpg"

            # Generate screenshot using ffmpeg
            cmd = [
                "ffmpeg",
                "-i", partial_video,
                "-ss", time,
                "-vframes", "1",
                screenshot_file
            ]
            subprocess.run(cmd, check=True)

            await client.send_photo(callback_query.from_user.id, photo=screenshot_file)

            # Clean up
            os.remove(screenshot_file)
            os.remove(partial_video)
            logging.info(f"Screenshot taken and sent at {time} seconds.")
        else:
            await callback_query.answer("Error: No video found to generate a screenshot from.")
            logging.error("No video found in the message for screenshot generation.")
    
    except Exception as e:
        logging.error(f"Error taking screenshot: {e}")
        await callback_query.answer("Error while taking the screenshot.")


@Client.on_callback_query(filters.regex(r"sample_video_(\d+)sec"))
async def create_sample_video(client, callback_query: CallbackQuery):
    try:
        if callback_query.message.video:
            time = callback_query.data.split("_")[2]
            logging.info(f"Generating sample video of {time} seconds.")

            # Download only the required portion of the video
            sample_video_file = f"sample_{time}.mp4"
            await download_partial_video(
                client,
                callback_query.message.video.file_id,
                duration=int(time),
                output_file=sample_video_file
            )

            await client.send_video(callback_query.from_user.id, video=sample_video_file)

            # Clean up
            os.remove(sample_video_file)
            logging.info(f"Sample video created and sent at {time} seconds.")
        else:
            await callback_query.answer("Error: No video found to generate a sample video from.")
            logging.error("No video found in the message for sample video generation.")
    
    except Exception as e:
        logging.error(f"Error creating sample video: {e}")
        await callback_query.answer("Error while creating the sample video.")
