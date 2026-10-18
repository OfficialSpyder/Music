from telethon import events, Button

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/help$"))
    async def help_handler(event):
        help_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  🛠️ **MASTER PROTOCOL DIRECTORY** 🛠️  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🎵 **[ AUDIO & VIDEO STREAMING ]**\n"
            " • `/play <query>` - Stream audio in voice chat\n"
            " • `/vplay <query>` - Stream video in voice chat\n"
            " • `/stop` or `/end` - Terminate stream & clear queue\n"
            " • `/speedtest` - Run server network diagnostics\n\n"
            "🛡️ **[ GROUP MODERATION ]**\n"
            " • `/ban` / `/unban` - Restrict or restore user access\n"
            " • `/mute` / `/unmute` - Control voice/chat permissions\n"
            " • `/promote` / `/demote` - Manage admin privileges\n\n"
            "⚡ **[ SYSTEM TELEMETRY ]**\n"
            " • `/ping` - Check server latency status\n"
            " • `/stats` - Fetch core node statistics\n"
            " • `/id` / `/userinfo` - Inspect target entity details\n\n"
            "👑 **[ GLOBAL PROTOCOLS ]**\n"
            " • `/gban` - Global network ban execution\n"
            " • `/gmute` - Global network mute execution\n\n"
            "💡 *Queue limit is set to 100 tracks with automatic anti-ban rest protection.*"
        )
        
        buttons = [
            [Button.url("💬 SUPPORT CHANNEL", "https://t.me/Master_Support_GC"), Button.url("📡 UPDATES", "https://t.me/Your_Official_Master")],
            [Button.url("👑 DEVELOPER", "https://t.me/I_AM_REAL_MASTER")]
        ]
        
        await event.reply(help_text, buttons=buttons, parse_mode='md')