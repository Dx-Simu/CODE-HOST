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
RENDER_URL = "https://code-host.onrender.com" # <--- Ekhane host korar por link ta bosiye deben

# --- DATABASE SETUP ---
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["DX_ID"]
users_col = db["users"]
groups_col = db["groups"]

app = Client("JoinRemoverBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- KEEP ALIVE SYSTEM (RENDER) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "NIKO (JOIN REMOVER BOT) IS ACTIVE!"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    """Bot nije nijeke protik 5 minute ontor ping korbe jeno off na hoy"""
    while True:
        try:
            time.sleep(300) # 5 Minutes
            if "onrender.com" in RENDER_URL:
                requests.get(RENDER_URL)
                print("Pinged self to stay active! ✅")
        except Exception as e:
            print(f"Ping Error: {e}")

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

# --- HANDLERS ---

@app.on_message(filters.service & filters.group)
async def delete_service_msgs(_, message: Message):
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    user_id = message.from_user.id
    if not await users_col.find_one({"_id": user_id}):
        await users_col.insert_one({"_id": user_id, "username": message.from_user.username})

    if not await is_subscribed(user_id):
        buttons = [
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 1", url=f"https://t.me/{CHANNELS[0]}")],
            [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 2", url=f"https://t.me/{CHANNELS[1]}")],
            [InlineKeyboardButton("ᴠᴇʀɪғʏ", callback_data="verify_user")]
        ]
        await message.reply_text(
            f"<b>ʜᴇʟʟᴏ {message.from_user.mention}! 👋</b>\n\n"
            f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b>.\n\n"
            f"ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.\n\n"
            f"<b>ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    await message.reply_text(
        f"<b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ! ✨</b>\n\nɪ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴀʟʟ sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.\n\n"
        f"<b>ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.me.username}?startgroup=true")]])
    )

@app.on_callback_query(filters.regex("verify_user"))
async def verify_callback(_, query):
    if await is_subscribed(query.from_user.id):
        await query.message.edit_text(
            f"<b>ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ! ✅</b>\n\nᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ.\n\n"
            f"<b>ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.me.username}?startgroup=true")]])
        )
    else:
        await query.answer("⚠️ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs!", show_alert=True)

@app.on_message(filters.new_chat_members)
async def on_join_group(_, message: Message):
    if any(m.id == (await app.get_me()).id for m in message.new_chat_members):
        if not await groups_col.find_one({"_id": message.chat.id}):
            await groups_col.insert_one({"_id": message.chat.id, "title": message.chat.title})
        await message.reply_text(f"<b>{BOT_NAME} sᴛᴀʀᴛᴇᴅ! 🛡️</b>\n\n<b>ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>")

@app.on_message(filters.command("user") & filters.user(OWNER_ID))
async def export_users(_, message: Message):
    msg = await message.reply_text("<code>ᴘʀᴏᴄᴇssɪɴɢ...</code>")
    count_u = await users_col.count_documents({})
    count_g = await groups_col.count_documents({})
    
    content = f"COUNT: {count_u + count_g}\n\n"
    content += "--- DATA ---\n"
    async for u in users_col.find({}): content += f"U: {u['_id']} | @{u.get('username','N/A')}\n"
    async for g in groups_col.find({}): content += f"G: {g['_id']} | {g.get('title','N/A')}\n"
        
    with open("database.txt", "w", encoding="utf-8") as f: f.write(content)
    await message.reply_document("database.txt", caption=f"<b>ᴅᴀᴛᴀʙᴀsᴇ ᴇxᴘᴏʀᴛᴇᴅ 📁\nᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>")
    os.remove("database.txt")
    await msg.delete()

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
    
    reply = message.reply_to_message
    msg = await message.reply_text("<code>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</code>")
    
    ids = []
    async for u in users_col.find({}): ids.append(u["_id"])
    async for g in groups_col.find({}): ids.append(g["_id"])
    
    text = reply.text or reply.caption or ""
    parsed_btns = parse_buttons(text)
    btn = InlineKeyboardMarkup(parsed_btns) if parsed_btns else None
    clean_text = re.sub(r"\[.+?\|.+?\]", "", text).strip()
    
    success = 0
    for target in list(set(ids)):
        try:
            await reply.copy(target, caption=clean_text if clean_text else None, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
            success += 1
            await asyncio.sleep(0.3)
        except: pass

    await msg.edit_text(f"<b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ! ✅</b>\n\nᴛᴏᴛᴀʟ: {success}\n<b>ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <code>{DEVELOPER}</code>")

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=keep_alive).start()
    print("Bot is starting...")
    app.run()
