import os
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from pyrogram import Client, filters

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

@Client.on_callback_query(filters.regex("generate_sample_video"))
async def generate_sample_video(client, callback_query):
    try:
        video_file_path = callback_query.message.video.file_id
        sample_file_path = f"/tmp/sample_{os.path.basename(video_file_path).split('.')[0]}.mp4"

        # Generate sample video using ffmpeg from stream
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        stream_url = await client.get_file_url(video_file_path)
        subprocess.run([ffmpeg_path, '-ss', '00:00:00', '-i', stream_url, '-t', '00:00:20', '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', sample_file_path], check=True)

        # Send the generated sample video
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=sample_file_path,
            caption="Here is your sample video (20 seconds)."
        )

        # Clean up
        os.remove(sample_file_path)
        logger.info("Sample video generated and sent successfully.")
    except Exception as e:
        logger.error(f"Error generating sample video: {e}")
        await callback_query.answer("Failed to generate sample video.")
