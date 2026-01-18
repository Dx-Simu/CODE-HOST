import os
import sys
import asyncio
import shutil
import logging
import time
import random
import string
import aiofiles # Async file handling for speed
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified, FloodWait
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIG ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8113879008:AAGEZaE4v7OZGguk_g-J9qbRm2-yYpiwXc0"
OWNER_ID = 6703335929
MONGO_URI = "mongodb+srv://darkgangdarks_db_user:aEEYR59YEVameS1y@cluster0.iyakwh0.mongodb.net/?appName=Cluster0"
DB_NAME = "CODE_HOST"
PORT = int(os.environ.get("PORT", 8080))

# --- STYLING ---
def to_small_caps(text):
    mapping = {'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'}
    return "".join(mapping.get(c.lower(), c) for c in text)

# --- DB & BOT ---
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
sudo_col = db["sudo_users"]
app = Client("Niko_Host", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_sessions = {}
active_procs = {}

async def is_auth(uid):
    if uid == OWNER_ID: return True
    return await sudo_col.find_one({"user_id": uid}) is not None

# --- COMMANDS ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await is_auth(message.from_user.id): return
    
    txt = f"<b>👋 {to_small_caps('Welcome Master')}!</b>\n\n<blockquote>I am <b>NIKO</b> by DX-CODEX.\nAdvanced Python Hosting Engine.</blockquote>"
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🚀 {to_small_caps('Host Python')}", callback_data="host_init")],
        [InlineKeyboardButton(f"📂 {to_small_caps('My Projects')}", callback_data="my_projs")]
    ])
    await message.reply(txt, reply_markup=btns)

@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def sudo_cmd(client, message):
    args = message.text.split()
    if len(args) < 3: return
    uid = int(args[2])
    if args[1] == "add":
        await sudo_col.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
        await message.reply("✅ Added.")
    elif args[1] == "remove":
        await sudo_col.delete_one({"user_id": uid})
        await message.reply("🗑 Removed.")

# --- CALLBACKS (OPTIMIZED) ---
@app.on_callback_query()
async def cb_handler(client, cb: CallbackQuery):
    await cb.answer() # INSTANT RESPONSE - FIXES LAG
    data = cb.data
    uid = cb.from_user.id

    if data == "host_init":
        pid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        path = f"projects/{pid}"
        os.makedirs(path, exist_ok=True)
        user_sessions[uid] = {"state": "file", "path": path, "id": pid}
        await cb.message.edit(f"<b>📂 {to_small_caps('Project')}:</b> <code>{pid}</code>\n\nSend .py file or paste code.")

    elif data == "my_projs":
        if not os.path.exists("projects"): return await cb.answer("Empty", show_alert=True)
        projs = os.listdir("projects")
        if not projs: return await cb.answer("No Projects", show_alert=True)
        kb = [[InlineKeyboardButton(f"📁 {p}", callback_data=f"view_{p}")] for p in projs]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="home")])
        await cb.message.edit(f"<b>🗂 {to_small_caps('Your Projects')}</b>", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("view_"):
        pid = data.split("_")[1]
        path = f"projects/{pid}"
        files = os.listdir(path) if os.path.exists(path) else []
        txt = f"<b>📂 ID:</b> <code>{pid}</code>\n\n" + "\n".join([f"📄 {f}" for f in files])
        kb = [[InlineKeyboardButton("▶️ Run", callback_data=f"run_{pid}_main.py")], 
              [InlineKeyboardButton("🗑 Delete", callback_data=f"del_{pid}")],
              [InlineKeyboardButton("🔙 Back", callback_data="my_projs")]]
        await cb.message.edit(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("del_"):
        pid = data.split("_")[1]
        shutil.rmtree(f"projects/{pid}", ignore_errors=True)
        await cb.answer("🗑 Deleted", show_alert=True)
        await cb.message.edit("Project removed.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="my_projs")]]))

    elif data.startswith("run_"):
        _, pid, file = data.split("_")
        await run_engine(client, cb, pid, file)

    elif data == "home":
        await start(client, cb.message)

# --- ASYNC FILE RECEIVE ---
@app.on_message(filters.private & (filters.document | filters.text))
async def uploader(client, message: Message):
    uid = message.from_user.id
    if uid not in user_sessions: return
    sess = user_sessions[uid]
    
    if sess["state"] == "file":
        if message.document and message.document.file_name.endswith(".py"):
            fpath = await message.download(file_name=sess["path"] + "/")
            sess["file"] = os.path.basename(fpath)
            await ask_req(message, sess)
        elif message.text:
            sess["tmp_code"] = message.text
            sess["state"] = "name"
            await message.reply("📝 Enter filename (e.g. main.py):")

    elif sess["state"] == "name":
        fname = message.text if message.text.endswith(".py") else message.text + ".py"
        async with aiofiles.open(f"{sess['path']}/{fname}", mode='w') as f:
            await f.write(sess["tmp_code"])
        sess["file"] = fname
        await ask_req(message, sess)

    elif sess["state"] == "req":
        if message.document: await message.download(file_name=sess["path"] + "/requirements.txt")
        else:
            async with aiofiles.open(f"{sess['path']}/requirements.txt", mode='w') as f:
                await f.write(message.text)
        await finish_setup(message, sess)

async def ask_req(m, sess):
    sess["state"] = "req"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{sess['id']}")]])
    await m.reply("📦 Send requirements.txt or package names (e.g. requests telethon):", reply_markup=kb)

@app.on_callback_query(filters.regex(r"skip_(.+)"))
async def skip_req(c, cb):
    await cb.answer()
    sess = user_sessions.get(cb.from_user.id)
    if sess: await finish_setup(cb.message, sess)

async def finish_setup(m, sess):
    pid = sess["id"]
    await m.reply(f"✅ Setup Done for <code>{pid}</code>", 
                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Open Project", callback_data=f"view_{pid}")]]))
    user_sessions.pop(m.chat.id, None)

# --- LIVE CONSOLE ENGINE ---
async def run_engine(client, cb, pid, file):
    path = f"projects/{pid}"
    await cb.message.edit("🚀 <b>Initializing Console...</b>")
    
    # Pip install if req exists
    if os.path.exists(f"{path}/requirements.txt"):
        p = await asyncio.create_subprocess_shell(f"pip install -r {path}/requirements.txt")
        await p.wait()

    proc = await asyncio.create_subprocess_exec(
        sys.executable, f"{path}/{file}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=path
    )
    active_procs[pid] = proc
    log = ""
    last_upd = 0

    async def stream_logs(stream):
        nonlocal log, last_upd
        while True:
            line = await stream.readline()
            if not line: break
            log += line.decode()
            if len(log) > 3000: log = log[-3000:]
            if time.time() - last_upd > 3: # 3 sec throttle to avoid lag
                try:
                    await cb.message.edit(f"<b>🖥 {to_small_caps('Live Console')}</b>\n<pre>{log}</pre>")
                    last_upd = time.time()
                except: pass

    await asyncio.gather(stream_logs(proc.stdout), stream_logs(proc.stderr))
    await proc.wait()
    await cb.message.edit(f"<b>✅ {to_small_caps('Process Finished')}</b>\n<pre>{log[-3500:]}</pre>")

# --- RENDER KEEP ALIVE & MAIN ---
async def h(r): return web.Response(text="NIKO ACTIVE")

async def start_all():
    s = web.Application(); s.router.add_get("/", h)
    runner = web.AppRunner(s); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    await app.start()
    logger.info("NIKO STARTED")
    await idle()

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except: pass
    asyncio.get_event_loop().run_until_complete(start_all())
