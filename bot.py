# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from database.users_chats_db import db
from info import *
from utils import temp, get_shortlink  # Import get_shortlink
from typing import Union, Optional, AsyncGenerator
from Script import script
from datetime import date, datetime
from aiohttp import web
from plugins import web_server

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
TechVJBot.start()
loop = asyncio.get_event_loop()

# Function to check subscription
async def is_subscribed(bot, user_id, channels):
    btn = []
    for channel_id in channels:
        try:
            await bot.get_chat_member(channel_id, user_id)
        except UserNotParticipant:
            chat = await bot.get_chat(int(channel_id))
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            logging.error(f"Error in subscription check: {e}")
    return btn

# Function to generate and shorten streaming link
async def generate_stream_link(file_id):
    try:
        # Replace with actual logic to generate a streaming link
        raw_link = f"https://your-stream-server.com/{file_id}"
        logging.info(f"Generated raw link: {raw_link}")
        short_link = await get_shortlink(raw_link)  # Shorten the link
        logging.info(f"Generated short link: {short_link}")
        return short_link
    except Exception as e:
        logging.error(f"Error generating short link: {e}")
        return None

# Global handler for all private messages and channels
@TechVJBot.on_message(filters.private | filters.channel)
async def message_handler(client, message):
    try:
        if message.chat.type == 'channel' and (message.video or message.document):
            logging.info(f"Processing message from channel: {message.chat.id}")
            
            # Forward media to log channel
            forwarded_message = await message.forward(LOG_CHANNEL)
            logging.info(f"Forwarded message ID: {forwarded_message.id}")
            
            # Generate streaming link
            stream_link = await generate_stream_link(forwarded_message.id)
            
            if stream_link:
                # Add button with the streaming link
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📽 Stream Video", url=stream_link)]]
                )
                # Reply with the button
                await message.reply_text(
                    "Your streaming link is ready! 🎉",
                    reply_markup=reply_markup
                )
            else:
                await message.reply_text("⚠️ Failed to generate a streaming link. Please try again.")
        elif message.chat.type == 'private' and AUTH_CHANNEL:
            logging.info(f"Processing message from private chat: {message.chat.id}")
            
            # Check subscription
            channels = AUTH_CHANNEL + SECOND_AUTH_CHANNEL
            btn = await is_subscribed(client, message.from_user.id, channels)
            if btn:
                username = (await client.get_me()).username
                btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(
                    text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the required channels first, then click on Try Again. 😇</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            
            # Default response for private messages
            await message.reply_text("Hello! Send a video file to get a streaming link.")
        else:
            logging.info(f"Unhandled message type from chat: {message.chat.id}")
    except Exception as e:
        logging.error(f"Error in message handler: {e}")
        await message.reply_text("⚠️ An error occurred while processing your request. Please try again.")

# Bot startup logic
async def start():
    print('\n')
    print('Initializing Your Bot')
    bot_info = await TechVJBot.get_me()
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
