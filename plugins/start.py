import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from info import URL, LOG_CHANNEL, SHORTLINK, AUTH_CHANNEL
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

async def is_subscribed(bot, user_id, channels):
    for channel_id in channels:
        try:
            chat = await bot.get_chat(channel_id)
            member = await bot.get_chat_member(channel_id, user_id)
            print(f"Checked membership for {chat.title}: Status = {member.status}")  # Log the status
            
            if member.status in ['member', 'administrator', 'creator']:
                continue
        except UserNotParticipant:
            print(f"User {user_id} is not a participant in {channel_id}")  # Log if not a participant
            return False, chat  # Return the chat object for the invite link
        except Exception as e:
            print(f"Error checking membership for {channel_id}: {e}")
            return False, None
            
    return True, None  # Return True if user is a member of all channels

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if AUTH_CHANNEL:
        try:
            is_member, chat = await is_subscribed(client, message.from_user.id, AUTH_CHANNEL)
            if not is_member and chat:
                invite_link = chat.invite_link
                username = (await client.get_me()).username
                btn = [
                    [InlineKeyboardButton(f'Join {chat.title}', url=invite_link)],
                    [InlineKeyboardButton(" 🍁 More Bots Channel 🍁", url=f"https://t.me/Rockers_Bots")],
                    [InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")],
                ]
                await message.reply_text(
                    text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the Below 2 channel then click on try again button. 😇</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            print(f"Error in subscription check: {e}")

    # Add user to database if not already existing
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🍿main Update Channel 🍿", url="https://t.me/ROCKERSBACKUP"),
                                InlineKeyboardButton("more bots", url="https://t.me/Rockers_Bots"),
                               ]])
    
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
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
    
    fileName = quote_plus(get_name(log_msg))
    if not SHORTLINK:
        stream = f"{URL}watch/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}"
        download = f"{URL}{log_msg.id}/{fileName}?hash={get_hash(log_msg)}"
    else:
        stream = await get_shortlink(f"{URL}watch/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}")
        download = await get_shortlink(f"{URL}{log_msg.id}/{fileName}?hash={get_hash(log_msg)}")
        
    await log_msg.reply_text(
        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
            InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)
        ]])
    )

    rm = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👀 𝐰𝐚𝐭𝐜𝐡 𝐨𝐧𝐥𝐢𝐧𝐞 | 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐅𝐢𝐥𝐞 📥", url=stream),
            ]
        ]
    )
    
    msg_text = """<strong>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 by : @ROCKERSBACKUP @Rockers_Bots</strong>\n\n<strong>📂 Fɪʟᴇ ɴᴀᴍᴇ :</strong> <b>{}</b>\n\n<strong>📦 Fɪʟᴇ ꜱɪᴢᴇ :</strong> <b>{}</b>"""

    await message.reply_text(
        text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm
    )
