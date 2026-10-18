import logging
import asyncio
import time
from yt_dlp import YoutubeDL
from telethon import events, Button
from pytgcalls.types import AudioPiped, VideoPiped, AudioVideoPiped

try:
    from config import LOG_GROUP_ID
except ImportError:
    LOG_GROUP_ID = None

logger = logging.getLogger("TgMusicBot")

# Anti-Ban & Continuous Playback Trackers
STREAM_START_TIME = {}
ACTIVE_DURATION_LIMIT = 3 * 3600  # 3 hours continuous play ke baad 5 min rest

def get_stream_url(query: str, is_video: bool = False):
    ydl_opts = {
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]' if is_video else 'bestaudio/best',
        'geo_bypass': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'prefer_ffmpeg': True,
        'socket_timeout': 30,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'default_search': 'ytsearch',
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info: 
                info = info['entries'][0]
            return {
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration_string', 'Unknown'),
                'url': info.get('url'),
            }
        except Exception as e:
            logger.error(f"Stream extraction error: {e}")
            return None

def register(client, pytgcalls=None, QUEUES=None, VQUEUES=None, **kwargs):
    QUEUES = QUEUES if QUEUES is not None else {}
    VQUEUES = VQUEUES if VQUEUES is not None else {}

    @client.on(events.NewMessage(pattern=r"^/(play|vplay)(?: (.+))?$"))
    async def play_stream_handler(event):
        mode = event.pattern_match.group(1)
        query = event.pattern_match.group(2)
        is_video = (mode == "vplay")

        if not query:
            return await event.reply(f"⚠️ Please provide a query!\n*Example:* `/{mode} Faded Alan Walker`")

        chat_id = event.chat_id
        target_dict = VQUEUES if is_video else QUEUES
        
        # Queue Limit Check (Max 100 tracks)
        if chat_id in target_dict and len(target_dict[chat_id]) >= 100:
            return await event.reply("⚠️ **Queue is full!** Maximum limit of 100 tracks reached.")

        msg = await event.reply(f"🔍 Searching & Buffering {'Video' if is_video else 'Audio'} Stream...")
        track = get_stream_url(query, is_video=is_video)
        if not track or not track['url']:
            return await msg.edit("❌ Stream retrieval failed. Try another query.")

        if chat_id not in target_dict: 
            target_dict[chat_id] = []
        target_dict[chat_id].append(track)

        buttons = [
            [Button.inline("⏸ Pause", data="pause"), Button.inline("▶️ Resume", data="resume")],
            [Button.inline("⏭ Skip", data="skip"), Button.inline("⏹ End", data="end")]
        ]

        if len(target_dict[chat_id]) == 1:
            try:
                # Anti-Ban Auto-Rest Check
                global STREAM_START_TIME
                current_time = time.time()
                if chat_id in STREAM_START_TIME and (current_time - STREAM_START_TIME[chat_id]) > ACTIVE_DURATION_LIMIT:
                    await event.respond("🛡️ **Anti-Ban Shield:** Bot has been running continuously. Taking a mandatory 5-minute rest to protect the account from Telegram flood limits...")
                    await asyncio.sleep(300)  # 5 minutes rest
                    STREAM_START_TIME[chat_id] = time.time()
                else:
                    STREAM_START_TIME[chat_id] = current_time

                # Using AudioVideoPiped for video + audio streaming simultaneously
                await pytgcalls.join_group_call(
                    chat_id,
                    AudioVideoPiped(track['url']) if is_video else AudioPiped(track['url'])
                )
                
                sender_name = "User"
                sender_id = None
                try:
                    sender = await event.get_sender()
                    if sender:
                        sender_name = getattr(sender, 'first_name', 'User')
                        sender_id = sender.id
                except Exception:
                    pass

                caption = (
                    f"▶️ **Now Streaming ({mode.upper()})**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎵 **Title:** `{track['title']}`\n"
                    f"⏱️ **Duration:** `{track['duration']}`\n"
                    f"👥 **Requested By:** {sender_name}"
                )
                await msg.edit(caption, buttons=buttons)

                # Send log to LOG_GROUP if configured
                if LOG_GROUP_ID:
                    log_text = (
                        "🎵 **#MUSIC_LOG: STREAM STARTED**\n\n"
                        f"👥 **Chat:** `{event.chat.title if event.is_group else 'Private'}` (`{chat_id}`)\n"
                        f"🎧 **Track:** `{track['title']}`\n"
                        f"⏱️ **Duration:** `{track['duration']}`\n"
                        f"👤 **Requested By:** `{sender_name}` (`{sender_id}`)"
                    )
                    await event.client.send_message(LOG_GROUP_ID, log_text)

            except Exception as e:
                logger.error(f"PyTgCalls execution error: {e}")
                await msg.edit(f"⚠️ PyTgCalls Error: `{e}`")
        else:
            await msg.edit(f"➕ Added to Queue ({len(target_dict[chat_id])}/100): `{track['title']}`")

    @client.on(events.NewMessage(pattern=r"^/skip$"))
    async def skip_handler(event):
        chat_id = event.chat_id
        is_video = chat_id in VQUEUES and len(VQUEUES[chat_id]) > 0
        target_dict = VQUEUES if is_video else QUEUES

        if chat_id not in target_dict or len(target_dict[chat_id]) == 0:
            return await event.reply("⚠️ Queue is empty!")

        skipped = target_dict[chat_id].pop(0)

        if len(target_dict[chat_id]) > 0:
            next_track = target_dict[chat_id][0]
            try:
                await pytgcalls.join_group_call(
                    chat_id,
                    AudioVideoPiped(next_track['url']) if is_video else AudioPiped(next_track['url'])
                )
                await event.reply(f"⏭ **Skipped:** `{skipped['title']}`\n▶️ **Now Playing:** `{next_track['title']}`")
                
                if LOG_GROUP_ID:
                    admin_user = await event.get_sender()
                    log_text = (
                        "⏭ **#MUSIC_LOG: TRACK SKIPPED**\n\n"
                        f"👥 **Chat:** `{event.chat.title if event.is_group else 'Private'}` (`{chat_id}`)\n"
                        f"❌ **Skipped:** `{skipped['title']}`\n"
                        f"▶️ **Now Playing:** `{next_track['title']}`\n"
                        f"👮 **Action By:** `{getattr(admin_user, 'first_name', 'User')}` (`{admin_user.id}`)"
                    )
                    await event.client.send_message(LOG_GROUP_ID, log_text)
            except Exception as e:
                await event.reply(f"⚠️ Error playing next track: `{e}`")
        else:
            try:
                await pytgcalls.leave_group_call(chat_id)
                await event.reply(f"⏭ **Skipped:** `{skipped['title']}`\n⏹️ **Queue empty. Left voice chat.**")
                
                if LOG_GROUP_ID:
                    admin_user = await event.get_sender()
                    log_text = (
                        "⏹️ **#MUSIC_LOG: STREAM FINISHED & LEFT**\n\n"
                        f"👥 **Chat:** `{event.chat.title if event.is_group else 'Private'}` (`{chat_id}`)\n"
                        f"👮 **Action By:** `{getattr(admin_user, 'first_name', 'User')}` (`{admin_user.id}`)"
                    )
                    await event.client.send_message(LOG_GROUP_ID, log_text)
            except Exception as e:
                await event.reply(f"Error: {e}")

    @client.on(events.NewMessage(pattern=r"^/(end|stop)$"))
    async def end_handler(event):
        chat_id = event.chat_id
        try:
            if chat_id in QUEUES:
                QUEUES[chat_id].clear()
            if chat_id in VQUEUES:
                VQUEUES[chat_id].clear()
            await pytgcalls.leave_group_call(chat_id)
            await event.reply("⏹️ **Stream Terminated & Queue Cleared. Voice Chat Left.**")
            
            if LOG_GROUP_ID:
                admin_user = await event.get_sender()
                log_text = (
                    "⏹️ **#MUSIC_LOG: STREAM TERMINATED**\n\n"
                    f"👥 **Chat:** `{event.chat.title if event.is_group else 'Private'}` (`{chat_id}`)\n"
                    f"👮 **Action By:** `{getattr(admin_user, 'first_name', 'User')}` (`{admin_user.id}`)"
                )
                await event.client.send_message(LOG_GROUP_ID, log_text)
        except Exception as e:
            await event.reply(f"Error: {e}")

    @client.on(events.CallbackQuery(data=b"pause"))
    async def pause_cb(event):
        try:
            await pytgcalls.pause(event.chat_id)
            await event.answer("⏸ Stream Paused!", alert=False)
        except Exception:
            await event.answer("⚠️ Active stream nahi mila.", alert=True)

    @client.on(events.CallbackQuery(data=b"resume"))
    async def resume_cb(event):
        try:
            await pytgcalls.resume(event.chat_id)
            await event.answer("▶️ Stream Resumed!", alert=False)
        except Exception:
            await event.answer("⚠️ Stream paused nahi hai.", alert=True)

    @client.on(events.CallbackQuery(data=b"skip"))
    async def skip_cb(event):
        chat_id = event.chat_id
        is_video = chat_id in VQUEUES and len(VQUEUES[chat_id]) > 0
        target_dict = VQUEUES if is_video else QUEUES
        if chat_id in target_dict and len(target_dict[chat_id]) > 0:
            target_dict[chat_id].pop(0)
            if len(target_dict[chat_id]) > 0:
                next_track = target_dict[chat_id][0]
                await pytgcalls.join_group_call(
                    chat_id,
                    AudioVideoPiped(next_track['url']) if is_video else AudioPiped(next_track['url'])
                )
                await event.edit(f"⏭ **Skipped to:** `{next_track['title']}`")
            else:
                await pytgcalls.leave_group_call(chat_id)
                await event.edit("⏹️ **Queue finished. Left voice chat.**")
        else:
            await event.answer("⚠️ Queue is empty!", alert=True)

    @client.on(events.CallbackQuery(data=b"end"))
    async def end_cb(event):
        try:
            if event.chat_id in QUEUES:
                QUEUES[event.chat_id].clear()
            if event.chat_id in VQUEUES:
                VQUEUES[event.chat_id].clear()
            await pytgcalls.leave_group_call(event.chat_id)
            await event.edit("⏹️ **Stream Terminated & Queue Cleared.**")
        except Exception as e:
            await event.answer(f"Error: {e}", alert=True)