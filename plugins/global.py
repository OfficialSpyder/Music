import logging
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

try:
    from config import LOG_GROUP_ID, SUDO_USERS
except ImportError:
    LOG_GROUP_ID = None
    SUDO_USERS = []

logger = logging.getLogger("TgMusicBot")

# Global memory storage for gban/gmute if database is not used
GBANNED_USERS = set()
GMUTED_USERS = set()

def register(client, **kwargs):
    owner_id = None

    async def is_sudo(event):
        nonlocal owner_id
        if not owner_id:
            try:
                me = await client.get_me()
                owner_id = me.id
            except Exception:
                owner_id = None
        
        # Check if sender is owner or listed in SUDO_USERS config
        sender_id = event.sender_id
        sudo_list = SUDO_USERS if isinstance(SUDO_USERS, list) else []
        return sender_id == owner_id or sender_id in sudo_list

    @client.on(events.NewMessage(pattern=r"^/gban$"))
    async def gban_handler(event):
        if not await is_sudo(event):
            return await event.reply("⚠️ **Access Denied:** This is a restricted Sudo/Owner command.")
        
        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ Reply to a user's message to execute a global ban.")
        
        target_id = reply.sender_id
        if target_id == event.sender_id:
            return await event.reply("⚠️ You cannot gban yourself!")

        msg = await event.reply("🚨 Executing Global Synchronization Ban across clusters...")
        
        success_count = 0
        fail_count = 0
        GBANNED_USERS.add(target_id)

        # Iterate through common dialogs/groups where bot has admin rights to ban
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    # Restrict/Ban user in chat
                    banned_rights = ChatBannedRights(
                        until_date=None,
                        view_messages=True,
                        send_messages=True,
                        send_media=True,
                        send_stickers=True,
                        send_gifs=True,
                        send_games=True,
                        send_inline=True,
                        embed_links=True
                    )
                    await client(EditBannedRequest(dialog.id, target_id, banned_rights))
                    success_count += 1
                except Exception:
                    fail_count += 1

        await msg.edit(
            f"🚨 **Global Ban Executed Successfully!**\n\n"
            f"👤 **Target ID:** `{target_id}`\n"
            f"🌐 **Banned in Groups:** `{success_count}` chats\n"
            f"⚠️ **Skipped/Failed:** `{fail_count}` chats"
        )

        # Send log to LOG_GROUP if configured
        if LOG_GROUP_ID:
            try:
                target_user = await client.get_entity(target_id)
                admin_user = await event.get_sender()
                log_text = (
                    "🚨 **#GLOBAL_LOG: GBAN EXECUTED**\n\n"
                    f"👤 **Target:** `{getattr(target_user, 'first_name', 'User')}` (`{target_id}`)\n"
                    f"🌐 **Affected Chats:** `{success_count}`\n"
                    f"👮 **Sudo Admin:** `{getattr(admin_user, 'first_name', 'Admin')}` (`{admin_user.id}`)"
                )
                await client.send_message(LOG_GROUP_ID, log_text)
            except Exception:
                pass

    @client.on(events.NewMessage(pattern=r"^/gmute$"))
    async def gmute_handler(event):
        if not await is_sudo(event):
            return await event.reply("⚠️ **Access Denied:** This is a restricted Sudo/Owner command.")
        
        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ Reply to a user's message to execute a global mute.")
        
        target_id = reply.sender_id
        if target_id == event.sender_id:
            return await event.reply("⚠️ You cannot gmute yourself!")

        GMUTED_USERS.add(target_id)
        await event.reply(f"🔇 **Global Mute broadcasted successfully for ID `{target_id}` across all active clusters.**")

        if LOG_GROUP_ID:
            try:
                target_user = await client.get_entity(target_id)
                admin_user = await event.get_sender()
                log_text = (
                    "🔇 **#GLOBAL_LOG: GMUTE EXECUTED**\n\n"
                    f"👤 **Target:** `{getattr(target_user, 'first_name', 'User')}` (`{target_id}`)\n"
                    f"👮 **Sudo Admin:** `{getattr(admin_user, 'first_name', 'Admin')}` (`{admin_user.id}`)"
                )
                await client.send_message(LOG_GROUP_ID, log_text)
            except Exception:
                pass

    # Auto-enforcement listener for gmuted users speaking in any chat
    @client.on(events.NewMessage)
    async def auto_gmute_enforcement(event):
        if event.sender_id in GMUTED_USERS and event.is_group:
            try:
                await event.delete()
            except Exception:
                pass