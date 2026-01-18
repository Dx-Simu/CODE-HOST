import os
import sys
import asyncio
import shutil
import logging
import time
import random
import string
import traceback
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8113879008:AAGEZaE4v7OZGguk_g-J9qbRm2-yYpiwXc0"
OWNER_ID = 6703335929
MONGO_URI = "mongodb+srv://darkgangdarks_db_user:aEEYR59YEVameS1y@cluster0.iyakwh0.mongodb.net/?appName=Cluster0"
DB_NAME = "CODE_HOST"
PORT = int(os.environ.get("PORT", 8080))

# --- STYLING FONTS ---
def to_small_caps(text):
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ',
        'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
        'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return "".join(mapping.get(c, c) for c in text)

# --- DATABASE SETUP ---
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
sudo_collection = db["sudo_users"]
projects_collection = db["projects"]

# --- BOT SETUP ---
app = Client("Niko_Host_Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- GLOBAL STATES ---
# Format: {user_id: {"state": "waiting_file", "path": "path/to/folder"}}
user_sessions = {}
# Active processes: {project_id: process_object}
active_processes = {}

# --- HELPER FUNCTIONS ---

async def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    user = await sudo_collection.find_one({"user_id": user_id})
    return True if user else False

def get_random_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- WEB SERVER (KEEP ALIVE) ---
async def web_server():
    async def handle(request):
        return web.Response(text="NIKO HOSTING BOT IS RUNNING...")

    webapp = web.Application()
    webapp.router.add_get('/', handle)
    runner = web.AppRunner(webapp)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web server started on port {PORT}")

# --- BOT COMMANDS ---

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    if not await is_authorized(message.from_user.id):
        return await message.reply(f"<b>⛔ {to_small_caps('Access Denied')}</b>\n<blockquote>You are not authorized to use this bot.</blockquote>")
    
    txt = (
        f"<b>👋 {to_small_caps('Welcome Master')}!</b>\n\n"
        f"<blockquote>I am <b>NIKO</b>, your advanced Python Hosting Assistant.\n"
        f"I can host, run, and manage your Python scripts securely.</blockquote>\n\n"
        f"<b>🛠 {to_small_caps('System Status')}:</b> <code>Active 🟢</code>\n"
        f"<b>📂 {to_small_caps('Hosting Engine')}:</b> <code>Python 3</code>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🚀 {to_small_caps('Host Python Web')}", callback_data="host_start")],
        [InlineKeyboardButton(f"📂 {to_small_caps('My Projects')}", callback_data="list_projects"),
         InlineKeyboardButton(f"⚙️ {to_small_caps('Sudo Manager')}", callback_data="sudo_help")]
    ])
    
    await message.reply_animation(
        animation="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHl5bnZ5aHl5bnZ5/3o7qE1YN7aQfVUTtlW/giphy.gif", # Just a placeholder tech gif
        caption=txt,
        reply_markup=buttons
    )

# --- SUDO COMMANDS ---
@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def sudo_handler(client, message):
    try:
        cmd = message.text.split()
        if len(cmd) < 3:
            return await message.reply("<b>⚠️ Usage:</b> `/sudo add <user_id>` or `/sudo remove <user_id>`")
        
        action = cmd[1].lower()
        target_id = int(cmd[2])
        
        if action == "add":
            await sudo_collection.update_one({"user_id": target_id}, {"$set": {"user_id": target_id}}, upsert=True)
            await message.reply(f"✅ <b>{to_small_caps('User Added')}</b> to Sudo list.")
        elif action == "remove":
            await sudo_collection.delete_one({"user_id": target_id})
            await message.reply(f"🗑 <b>{to_small_caps('User Removed')}</b> from Sudo list.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- HOSTING FLOW ---

@app.on_callback_query(filters.regex("host_start"))
async def host_init(client, cb: CallbackQuery):
    proj_id = get_random_id()
    folder_path = f"projects/{proj_id}"
    os.makedirs(folder_path, exist_ok=True)
    
    user_sessions[cb.from_user.id] = {"state": "waiting_file", "path": folder_path, "id": proj_id}
    
    await cb.message.edit(
        f"<b>📂 {to_small_caps('New Project Created')}</b>\n"
        f"🆔 ID: <code>{proj_id}</code>\n\n"
        f"<blockquote>Please send your <b>.py file</b> or <b>paste the code</b> in a message now.</blockquote>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="back_home")]])
    )

@app.on_message(filters.private & (filters.document | filters.text))
async def handle_uploads(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        return
    
    session = user_sessions[user_id]
    state = session.get("state")
    folder_path = session.get("path")
    
    # 1. HANDLE FILE/CODE UPLOAD
    if state == "waiting_file":
        filename = "main.py" # Default
        
        if message.document:
            if not message.document.file_name.endswith(".py"):
                return await message.reply("❌ Please send a valid <b>.py</b> file.")
            file_path = await message.download(file_name=os.path.join(folder_path, message.document.file_name))
            filename = message.document.file_name
        
        elif message.text:
            # If user sends code directly
            code = message.text
            session["temp_code"] = code
            session["state"] = "naming_file"
            return await message.reply(
                f"📝 <b>{to_small_caps('Code Received')}</b>.\n\n"
                f"Please enter the <b>Filename</b> (e.g., `script.py`):"
            )
        
        # Proceed after file download
        await prompt_requirements(message, folder_path, filename, session["id"])

    # 2. HANDLE FILENAME FOR TEXT CODE
    elif state == "naming_file":
        filename = message.text.strip()
        if not filename.endswith(".py"):
            filename += ".py"
        
        with open(os.path.join(folder_path, filename), "w") as f:
            f.write(session["temp_code"])
            
        await prompt_requirements(message, folder_path, filename, session["id"])

    # 3. HANDLE REQUIREMENTS (PIP)
    elif state == "waiting_req":
        if message.document and message.document.file_name == "requirements.txt":
            await message.download(file_name=os.path.join(folder_path, "requirements.txt"))
            await install_and_ready(message, folder_path, session["main_file"], session["id"])
        elif message.text:
            # Create requirements.txt from text
            with open(os.path.join(folder_path, "requirements.txt"), "w") as f:
                f.write(message.text)
            await install_and_ready(message, folder_path, session["main_file"], session["id"])

async def prompt_requirements(message, folder_path, main_file, proj_id):
    user_sessions[message.from_user.id]["state"] = "waiting_req"
    user_sessions[message.from_user.id]["main_file"] = main_file
    
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⏭ {to_small_caps('Skip / No Req')}", callback_data=f"skip_req_{proj_id}")]
    ])
    
    await message.reply(
        f"✅ <b>{main_file} Saved!</b>\n\n"
        f"📦 <b>{to_small_caps('Package Installation')}</b>\n"
        f"Send <code>pip install</code> command names OR send a <code>requirements.txt</code> file.\n"
        f"<i>(Example: requests pymongo)</i>",
        reply_markup=btn
    )

@app.on_callback_query(filters.regex(r"skip_req_(.+)"))
async def skip_requirements(client, cb):
    proj_id = cb.data.split("_")[2]
    user_id = cb.from_user.id
    if user_id in user_sessions and user_sessions[user_id]["id"] == proj_id:
        path = user_sessions[user_id]["path"]
        main_file = user_sessions[user_id]["main_file"]
        await install_and_ready(cb.message, path, main_file, proj_id, skip=True)

async def install_and_ready(message, folder_path, main_file, proj_id, skip=False):
    status_msg = await message.reply(f"⏳ <b>{to_small_caps('Processing Environment...')}</b>")
    
    if not skip:
        req_file = os.path.join(folder_path, "requirements.txt")
        if os.path.exists(req_file):
            proc = await asyncio.create_subprocess_shell(
                f"pip install -r {req_file}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
    
    # Ready to run
    user_sessions.pop(message.chat.id, None) # Clear session
    
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"▶️ {to_small_caps('Run File')}", callback_data=f"run_{proj_id}_{main_file}")],
        [InlineKeyboardButton(f"🗑 {to_small_caps('Delete Project')}", callback_data=f"del_{proj_id}")]
    ])
    
    await status_msg.edit(
        f"🎉 <b>{to_small_caps('Project Ready!')}</b>\n\n"
        f"📂 <b>ID:</b> <code>{proj_id}</code>\n"
        f"📄 <b>File:</b> <code>{main_file}</code>\n\n"
        f"<i>Click Run to start the live console.</i>",
        reply_markup=btns
    )

# --- RUNNING & LIVE CONSOLE ---

@app.on_callback_query(filters.regex(r"run_(.+)_(.+)"))
async def run_project(client, cb: CallbackQuery):
    _, proj_id, filename = cb.data.split("_")
    folder = f"projects/{proj_id}"
    file_path = os.path.join(folder, filename)
    
    await cb.message.edit(f"🚀 <b>{to_small_caps('Initializing Live Console...')}</b>")
    
    # Running the script
    process = await asyncio.create_subprocess_exec(
        sys.executable, file_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=folder # Run inside the project folder
    )
    
    active_processes[proj_id] = process
    
    # Console Loop
    output_buffer = ""
    start_time = time.time()
    last_edit = 0
    
    console_template = (
        f"<b>🖥 {to_small_caps('Live Console')}</b> | 🆔 `{proj_id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<pre language='bash'>{{}}</pre>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 <b>Running...</b> | <a href='https://t.me/DX_CODEX'>ᴅx-ᴄᴏᴅᴇx</a>"
    )

    stop_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 STOP", callback_data=f"stop_{proj_id}")]])
    msg = await cb.message.edit(console_template.format("..."), reply_markup=stop_btn)

    async def read_stream(stream):
        nonlocal output_buffer, last_edit
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode('utf-8', errors='ignore')
            output_buffer += decoded
            
            # Keep buffer size manageable (last 2000 chars)
            if len(output_buffer) > 2000:
                output_buffer = output_buffer[-2000:]

            now = time.time()
            if now - last_edit > 2: # Edit every 2 seconds to avoid flood wait
                try:
                    await msg.edit(console_template.format(output_buffer), reply_markup=stop_btn)
                    last_edit = now
                except MessageNotModified:
                    pass
                except Exception as e:
                    print(f"Edit error: {e}")

    await asyncio.gather(
        read_stream(process.stdout),
        read_stream(process.stderr)
    )
    
    await process.wait()
    
    final_status = "✅ Finished" if process.returncode == 0 else "❌ Crashed"
    await msg.edit(
        f"<b>🖥 {to_small_caps('Console Terminated')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<pre>{output_buffer[-3500:]}</pre>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Status:</b> {final_status}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="host_start")]])
    )
    if proj_id in active_processes:
        del active_processes[proj_id]

@app.on_callback_query(filters.regex(r"stop_(.+)"))
async def stop_process(client, cb):
    proj_id = cb.data.split("_")[1]
    if proj_id in active_processes:
        try:
            active_processes[proj_id].terminate()
            del active_processes[proj_id]
            await cb.answer("🛑 Process Stopping...", show_alert=True)
        except:
            await cb.answer("Error stopping.", show_alert=True)
    else:
        await cb.answer("Process already stopped.", show_alert=True)

# --- PROJECT MANAGEMENT ---

@app.on_callback_query(filters.regex("list_projects"))
async def list_projects(client, cb):
    if not os.path.exists("projects"):
        return await cb.answer("No projects found.", show_alert=True)
    
    projects = os.listdir("projects")
    if not projects:
        return await cb.answer("No projects found.", show_alert=True)
    
    buttons = []
    for p in projects:
        buttons.append([InlineKeyboardButton(f"📁 {p}", callback_data=f"view_{p}")])
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_home")])
    
    await cb.message.edit(
        f"<b>🗂 {to_small_caps('Your Projects')}</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"view_(.+)"))
async def view_project_files(client, cb):
    proj_id = cb.data.split("_")[1]
    folder = f"projects/{proj_id}"
    
    if not os.path.exists(folder):
        return await cb.answer("Project not found!", show_alert=True)
        
    files = os.listdir(folder)
    file_list = "\n".join([f"📄 {f}" for f in files])
    
    btns = [
        [InlineKeyboardButton("🗑 Delete Project", callback_data=f"del_{proj_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="list_projects")]
    ]
    
    await cb.message.edit(
        f"<b>📂 Project:</b> <code>{proj_id}</code>\n\n"
        f"{file_list}",
        reply_markup=InlineKeyboardMarkup(btns)
    )

@app.on_callback_query(filters.regex(r"del_(.+)"))
async def delete_project(client, cb):
    proj_id = cb.data.split("_")[1]
    folder = f"projects/{proj_id}"
    
    if os.path.exists(folder):
        shutil.rmtree(folder)
        await cb.answer("✅ Project Deleted!", show_alert=True)
        await list_projects(client, cb)
    else:
        await cb.answer("Already deleted.", show_alert=True)

@app.on_callback_query(filters.regex("back_home"))
async def back_home(client, cb):
    # Resetting the start message
    await start_command(client, cb.message)

# --- ENTRY POINT ---
if __name__ == "__main__":
    if not os.path.exists("projects"):
        os.makedirs("projects")
    
    # Start Web Server in Background
    loop = asyncio.get_event_loop()
    loop.create_task(web_server())
    
    print("🤖 NIKO IS STARTING...")
    app.run()
