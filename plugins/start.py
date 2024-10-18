import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from info import URL, LOG_CHANNEL, SHORTLINK, AUTH_CHANNEL, SECOND_AUTH_CHANNEL
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

async def is_subscribed(bot, user_id, channels):
    btn = []
    for channel_id in channels:
        try:
            chat = await bot.get_chat(int(channel_id))
            member = await bot.get_chat_member(channel_id, user_id)

            if member.status in ['member', 'administrator', 'creator']:
                print(f"User {user_id} is a member of {chat.title}.")
                continue
            else:
                btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
                print(f"User {user_id} is not a member of {chat.title}.")
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
            print(f"User {user_id} is not a participant of {chat.title}.")
        except ChatAdminRequired:
            print(f"Bot does not have permission to access {chat.title}.")
        except Exception as e:
            print(f"Error fetching member for {channel_id}: {e}")
    return btn

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    channels = AUTH_CHANNEL + SECOND_AUTH_CHANNEL

    if channels:
        try:
            btn = await is_subscribed(client, user_id, channels)
            if btn:
                username = (await client.get_me()).username
                btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(
                    text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join both channels then click on the try again button. 😇</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            else:
                print(f"User {user_id} is subscribed to all channels.")
        except Exception as e:
            print(f"Error in subscription check for user {user_id}: {e}")

    # Add user to database if not already existing
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user_id, message.from_user.mention))

    rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/vj_botz")]])

    await client.send_message(
        chat_id=user_id,
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
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)
            ]
        ]
    )

    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

    await message.reply_text(
        text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm
    )
