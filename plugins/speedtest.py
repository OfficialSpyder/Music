import time, aiohttp
from telethon import events

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/speedtest$"))
    async def speedtest_handler(event):
        msg = await event.reply("🚀 Running Cloudflare Bandwidth Test...")
        start = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://speed.cloudflare.com/__down?bytes=10000000") as resp:
                    ping = round((time.time() - start) * 1000, 2)
                    size_bits = len(await resp.read()) * 8
                    speed = round((size_bits / (time.time() - start)) / 1_000_000, 2)
            await msg.edit(f"⚡ **Speedtest Result:**\n📥 Download: `{speed} Mbps`\n🏓 Ping: `{ping} ms`")
        except Exception as e:
            await msg.edit(f"❌ Failed: `{e}`")