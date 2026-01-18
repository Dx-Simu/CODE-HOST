import os
import re
import asyncio
import requests
import time
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8270046107:AAHA3k62htFOPitlivuyDgx4aS7gjcqu0bo"
OWNER_ID = 6703335929
MONGO_URI = "mongodb+srv://darkgangdarks_db_user:aEEYR59YEVameS1y@cluster0.iyakwh0.mongodb.net/?appName=Cluster0"
CHANNELS = ["alphacodex369", "Termuxcodex"]

BOT_NAME = "ᴊᴏɪɴ ʀᴇᴍᴏᴠᴇʀ ʙᴏᴛ"
DEVELOPER = "ᴅx-ᴄᴏᴅᴇx"
RENDER_URL = "https://code-host.onrender.com"

# --- DATABASE SETUP ---
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["DX_ID"]
users_col = db["users"]
groups_col = db["groups"]

app = Client("JoinRemoverBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- KEEP ALIVE SYSTEM ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return f"{BOT_NAME} IS ONLINE BY {DEVELOPER}"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    while True:
        try:
            time.sleep(300)
            requests.get(RENDER_URL)
        except:
            pass

# --- HELPER FUNCTIONS ---
async def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            await app.get_chat_member(channel, user_id)
        except UserNotParticipant:
            return False
        except Exception:
            return False
    return True

def parse_buttons(text):
    buttons = []
    if not text: return None
    lines = text.split('\n')
    for line in lines:
        match = re.search(r"\[(.+?)\s*\|\s*(https?://.+)\]", line)
        if match:
            buttons.append([InlineKeyboardButton(match.group(1).strip(), url=match.group(2).strip())])
    return buttons if buttons else None

ADD_ME_LINK = f"https://t.me/{{}}?startgroup=true&admin=delete_messages+invite_users+manage_video_chats+manage_chat+pin_messages"

# --- HANDLERS ---

# Auto Service Message Remover
@app.on_message(filters.service & filters.group)
async def delete_service_msgs(_, message: Message):
    try:
        await message.delete()
    except:
        pass

# Start Command
@app.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    user_id = message.from_user.id
    if not await users_col.find_one({"_id": user_id}):
        await users_col.insert_one({"_id": user_id, "username": message.from_user.username})

    me = await app.get_me()
    add_link = ADD_ME_LINK.format(me.username)

    if not await is_subscribed(user_id):
        buttons = [
            [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 1", url=f"https://t.me/{CHANNELS[0]}")],
            [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 2", url=f"https://t.me/{CHANNELS[1]}")],
            [InlineKeyboardButton("💠 ᴠᴇʀɪғʏ 💠", callback_data="verify_user")]
        ]
        await message.reply_text(
            f"<b>👋 ʜᴇʟʟᴏ {message.from_user.mention}!</b>\n\n"
            f"<blockquote>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b>. ᴛᴏ ᴀᴄᴄᴇss ᴍʏ ᴘᴏᴡᴇʀғᴜʟ ғᴇᴀᴛᴜʀᴇs, ʏᴏᴜ ᴍᴜsᴛ sᴜʙsᴄʀɪʙᴇ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs.</blockquote>\n\n"
            f"<b>👤 ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    await message.reply_text(
        f"<b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {BOT_NAME} ✨</b>\n\n"
        f"<blockquote>ɪ ᴀᴍ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ᴄʟᴇᴀɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs. ᴀᴅᴅ ᴍᴇ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴅᴇʟᴇᴛᴇ ᴘᴇʀᴍɪssɪᴏɴ.</blockquote>\n\n"
        f"<b>🚀 sᴛᴀᴛᴜs:</b> <code>ᴀᴄᴛɪᴠᴇ</code>\n\n"
        f"<b>👤 ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=add_link)]
        ])
    )

# Group ID Save & Advanced Greeting Logic
@app.on_message(filters.new_chat_members)
async def on_join_group(_, message: Message):
    me = await app.get_me()
    # Check if the bot itself is added
    if any(m.id == me.id for m in message.new_chat_members):
        chat_id = message.chat.id
        chat_title = message.chat.title
        
        # Force Save to Database
        if not await groups_col.find_one({"_id": chat_id}):
            await groups_col.insert_one({"_id": chat_id, "title": chat_title})
            db_status = "✅ sᴀᴠᴇᴅ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ"
        else:
            db_status = "🔄 ᴀʟʀᴇᴀᴅʏ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ"
        
        # Advanced Style Greeting Message
        await message.reply_text(
            f"<b>🛡️ {BOT_NAME} ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ!</b>\n\n"
            f"<blockquote>ʜᴇʟʟᴏ ᴇᴠᴇʀʏᴏɴᴇ! ɪ ᴀᴍ ʏᴏᴜʀ ᴀᴅᴠᴀɴᴄᴇᴅ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇʀ. ɪ ᴡɪʟʟ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴀʟʟ sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇs ᴛᴏ ᴋᴇᴇᴘ ᴛʜɪs ᴄʜᴀᴛ ᴄʟᴇᴀɴ.</blockquote>\n\n"
            f"<b>📊 ɢʀᴏᴜᴘ ᴀɴᴀʟʏᴛɪᴄs:</b>\n"
            f"📝 ᴛɪᴛʟᴇ: <b>{chat_title}</b>\n"
            f"🆔 ɪᴅ: <code>{chat_id}</code>\n"
            f"📁 ᴅʙ: <b>{db_status}</b>\n\n"
            f"<b>⚠️ ɴᴏᴛᴇ:</b> ᴍᴀᴋᴇ sᴜʀᴇ ɪ ʜᴀᴠᴇ 'ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs' ᴘᴇʀᴍɪssɪᴏɴ!\n\n"
            f"<b>👤 ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>"
        )

# Callback & Other Commands (No changes below)
@app.on_callback_query(filters.regex("verify_user"))
async def verify_callback(_, query):
    me = await app.get_me()
    add_link = ADD_ME_LINK.format(me.username)
    if await is_subscribed(query.from_user.id):
        await query.message.edit_text(
            f"<b>✅ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ!</b>\n\n"
            f"<blockquote>ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴇɴᴊᴏʏ sᴇʀᴠɪᴄᴇs.</blockquote>\n\n"
            f"<b>👤 ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=add_link)]])
        )
    else:
        await query.answer("⚠️ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!", show_alert=True)

@app.on_message(filters.command("user") & filters.user(OWNER_ID))
async def export_users(_, message: Message):
    msg = await message.reply_text("<code>📊 ᴀɴᴀʟʏᴢɪɴɢ ᴅᴀᴛᴀʙᴀsᴇ...</code>")
    count_u = await users_col.count_documents({})
    count_g = await groups_col.count_documents({})
    content = f"📈 ᴛᴏᴛᴀʟ: {count_u + count_g}\n\n👤 Users: {count_u}\n👥 Groups: {count_g}\n\n"
    async for u in users_col.find({}): content += f"U: {u['_id']} | @{u.get('username','N/A')}\n"
    async for g in groups_col.find({}): content += f"G: {g['_id']} | {g.get('title','N/A')}\n"
    with open("database.txt", "w", encoding="utf-8") as f: f.write(content)
    await message.reply_document("database.txt", caption=f"<b>📁 ᴅᴀᴛᴀʙᴀsᴇ sᴛᴀᴛs</b>\n\n<b>ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>")
    os.remove("database.txt")
    await msg.delete()

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!</b>")
    reply = message.reply_to_message
    msg = await message.reply_text("<code>🚀 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</code>")
    ids = []
    async for u in users_col.find({}): ids.append(u["_id"])
    async for g in groups_col.find({}): ids.append(g["_id"])
    text = reply.text or reply.caption or ""
    btn = InlineKeyboardMarkup(parse_buttons(text)) if parse_buttons(text) else None
    clean_text = re.sub(r"\[.+?\|.+?\]", "", text).strip()
    success = 0
    for target in list(set(ids)):
        try:
            await reply.copy(target, caption=clean_text if clean_text else None, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
            success += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit_text(f"<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ!</b>\n\n✅ <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n<b>👤 ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>")

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=keep_alive).start()
    print("Bot is starting...")
    app.run()
