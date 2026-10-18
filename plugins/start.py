from telethon import events, Button
from config import START_IMG
import os

try:
    from config import LOG_GROUP_ID
except ImportError:
    LOG_GROUP_ID = None

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/start$"))
    async def start_handler(event):
        bot_username = (await client.get_me()).username
        
        # Elite Cyberpunk Rich Text Banner
        welcome_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  ⚡ **MASTER MUSIC PROTOCOL v5.0** ⚡  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "╔══════════════════════════════╗\n"
            "║  🌐 **SYSTEM STATUS:** `ONLINE`      ║\n"
            "║  🛡️ **SECURITY:** `ENCRYPTED`      ║\n"
            "║  🎧 **ENGINE:** `PYTGCALLS v0.9.7`   ║\n"
            "╚══════════════════════════════╝\n\n"
            "🔥 *Welcome to the next-generation decentralized audio and voice chat streaming daemon. Built for zero-latency, high-fidelity sound delivery.* \n\n"
            "👑 **Architect & Owner:** [MASTER](https://t.me/I_AM_REAL_Master)"
        )
        
        buttons = [
            [Button.url("🚀 • ADD TO YOUR GROUP • 🚀", f"https://t.me/{bot_username}?startgroup=true")],
            [Button.inline("⚙️ COMMANDS LIST", data="help_menu_callback")],
            [Button.url("📡 UPDATES", "https://t.me/Your_Official_Master"), Button.url("💬 SUPPORT", "https://t.me/Master_Support_GC")]
        ]
        
        # Send notification to LOG_GROUP if configured
        if LOG_GROUP_ID and not event.is_group:
            try:
                user = await event.get_sender()
                log_text = (
                    "🚀 **#BOT_LOG: NEW START EXECUTION**\n\n"
                    f"👤 **User:** `{getattr(user, 'first_name', 'User')}` (`{user.id}`)\n"
                    f"🔗 **Username:** @{getattr(user, 'username', 'None')}"
                )
                await event.client.send_message(LOG_GROUP_ID, log_text)
            except Exception:
                pass

        try:
            if START_IMG and (os.path.exists(START_IMG) or START_IMG.startswith("http")):
                await event.reply(file=START_IMG, message=welcome_text, buttons=buttons, parse_mode='md')
            else:
                await event.reply(welcome_text, buttons=buttons, parse_mode='md')
        except Exception:
            await event.reply(welcome_text, buttons=buttons, parse_mode='md')

    @client.on(events.CallbackQuery(data=b"help_menu_callback"))
    async def help_menu_cb(event):
        help_text = (
            "🛠️ **MASTER MUSIC BOT - COMMANDS DIRECTORY** 🛠️\n\n"
            "🎵 **Music Playback:**\n"
            " • `/play <query>` - Play audio in voice chat\n"
            " • `/vplay <query>` - Play video stream in voice chat\n"
            " • `/skip` - Skip to the next track in queue\n"
            " • `/end` or `/stop` - Stop stream and clear queue\n\n"
            "🛡️ **Group Moderation & Utilities:**\n"
            " • `/ban` - Ban a user from the chat\n"
            " • `/mute` - Mute a user in the chat\n"
            " • `/promote` - Promote a user to admin\n"
            " • `/ping` - Check system latency & status\n"
            " • `/speedtest` - Run server network speed test\n\n"
            "💡 *All queues support up to 100 tracks with automatic anti-ban rest protection!*"
        )
        await event.answer()
        await event.edit(help_text, buttons=[[Button.inline("« Back to Home", data="back_home")]]))

    @client.on(events.CallbackQuery(data=b"back_home"))
    async def back_home_cb(event):
        bot_username = (await client.get_me()).username
        welcome_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  ⚡ **MASTER MUSIC PROTOCOL v5.0** ⚡  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "╔══════════════════════════════╗\n"
            "║  🌐 **SYSTEM STATUS:** `ONLINE`      ║\n"
            "║  🛡️ **SECURITY:** `ENCRYPTED`      ║\n"
            "║  🎧 **ENGINE:** `PYTGCALLS v0.9.7`   ║\n"
            "╚══════════════════════════════╝\n\n"
            "🔥 *Welcome to the next-generation decentralized audio and voice chat streaming daemon.*"
        )
        buttons = [
            [Button.url("🚀 • ADD TO YOUR GROUP • 🚀", f"https://t.me/{bot_username}?startgroup=true")],
            [Button.inline("⚙️ COMMANDS LIST", data="help_menu_callback")],
            [Button.url("📡 UPDATES", "https://t.me/Your_Official_Master"), Button.url("💬 SUPPORT", "https://t.me/Master_Support_GC")]
        ]
        await event.answer()
        await event.edit(welcome_text, buttons=buttons, parse_mode='md')