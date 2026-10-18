import psutil, platform, time, sqlite3, logging
from telethon import events

logger = logging.getLogger("TgMusicBot")
BOT_START_TIME = time.time()
DB_FILE = "bot_chats.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER PRIMARY KEY, chat_title TEXT)')
    conn.commit()
    conn.close()
init_db()

def get_readable_time(seconds):
    count, ping_time, time_list = 0, "", []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if count == 3: remainder, result = divmod(seconds, 24)
        if time_list and not result:
            seconds = remainder; continue
        time_list.append(str(int(result)))
        seconds = remainder
    for x in range(len(time_list)): time_list[x] += time_suffix_list[x]
    if len(time_list) == 4: ping_time += time_list.pop() + " days, "
    time_list.reverse()
    return ping_time + ":".join(time_list)

def register(client, QUEUES=None, VQUEUES=None, **kwargs):
    QUEUES = QUEUES if QUEUES is not None else {}
    VQUEUES = VQUEUES if VQUEUES is not None else {}

    @client.on(events.NewMessage)
    async def track_chats(event):
        if event.is_group or event.is_channel:
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO chats (chat_id, chat_title) VALUES (?, ?)", (event.chat_id, getattr(event.chat, 'title', 'Group')))
                conn.commit(); conn.close()
            except Exception: pass

    @client.on(events.NewMessage(pattern=r"^/stats$"))
    async def stats_handler(event):
        msg = await event.reply("📊 **Fetching Global Telemetry...**")
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chats")
            total_chats = cursor.fetchone()[0] or 1
            conn.close()

            cpu = psutil.cpu_percent(interval=0.3)
            ram = psutil.virtual_memory()
            uptime = get_readable_time(int(time.time() - BOT_START_TIME))
            active_streams = len([c for c, q in QUEUES.items() if q]) + len([c for c, q in VQUEUES.items() if q])

            stats_text = (
                f"🔥 **MASTER BOT STATISTICS** 🔥\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 **Global Presence Chats:** `{total_chats}`\n"
                f"⏱️ **Uptime:** `{uptime}`\n"
                f"🎵 **Active Streams:** `{active_streams}`\n"
                f"🖥️ **CPU Load:** `{cpu}%`\n"
                f"🧠 **RAM Usage:** `{ram.percent}%`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            await msg.edit(stats_text)
        except Exception as e:
            await msg.edit(f"⚠️ Error: `{e}`")