import time
from telethon import events

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/ping$"))
    async def ping_handler(event):
        start = time.time()
        msg = await event.reply("🏓 **Pinging Daemon...**")
        end = time.time()
        latency = round((end - start) * 1000, 2)
        await msg.edit(f"🏓 **PONG!**\n`{latency}ms`")