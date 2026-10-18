from telethon import events

try:
    from config import LOG_GROUP_ID
except ImportError:
    LOG_GROUP_ID = None

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/ban$"))
    async def ban_handler(event):
        if not event.is_group:
            return await event.reply("⚠️ This command can only be used in groups!")
        
        # Check if the user executing the command is an admin or creator
        try:
            sender_perms = await event.client.get_permissions(event.chat_id, event.sender_id)
            if not sender_perms.is_admin and not sender_perms.is_creator:
                return await event.reply("❌ **Access Denied:** Only group admins or owners can use this command.")
        except Exception:
            return await event.reply("⚠️ Failed to verify administrative permissions.")

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ Reply to a user's message to ban them.")
        
        try:
            target_user = await event.client.get_entity(reply.sender_id)
            admin_user = await event.get_sender()
            
            # Prevent banning admins or bot itself
            target_perms = await event.client.get_permissions(event.chat_id, reply.sender_id)
            if target_perms.is_admin or target_perms.is_creator:
                return await event.reply("❌ **Error:** You cannot ban another administrator or group owner.")

            # Execute ban
            await event.client.edit_permissions(event.chat_id, reply.sender_id, view_messages=False)
            await event.reply("🔨 **User has been permanently banned from this chat.**")
            
            # Send log to LOG_GROUP if configured
            if LOG_GROUP_ID:
                log_text = (
                    "🛡️ **#MOD_LOG: USER BANNED**\n\n"
                    f"👥 **Chat:** `{event.chat.title}` (`{event.chat_id}`)\n"
                    f"🔨 **Target:** `{getattr(target_user, 'first_name', 'User')}` (`{reply.sender_id}`)\n"
                    f"👮 **Admin:** `{getattr(admin_user, 'first_name', 'Admin')}` (`{admin_user.id}`)"
                )
                await event.client.send_message(LOG_GROUP_ID, log_text)
                
        except Exception as e:
            await event.reply(f"❌ Error: `{e}`")

    @client.on(events.NewMessage(pattern=r"^/unban$"))
    async def unban_handler(event):
        if not event.is_group:
            return await event.reply("⚠️ This command can only be used in groups!")
        
        # Check if the user executing the command is an admin or creator
        try:
            sender_perms = await event.client.get_permissions(event.chat_id, event.sender_id)
            if not sender_perms.is_admin and not sender_perms.is_creator:
                return await event.reply("❌ **Access Denied:** Only group admins or owners can use this command.")
        except Exception:
            return await event.reply("⚠️ Failed to verify administrative permissions.")

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ Reply to a user to unban them.")
        
        try:
            target_user = await event.client.get_entity(reply.sender_id)
            admin_user = await event.get_sender()
            
            # Execute unban (Restoring view messages permission)
            await event.client.edit_permissions(event.chat_id, reply.sender_id, view_messages=True)
            await event.reply("🔓 **User ban has been lifted successfully.**")
            
            # Send log to LOG_GROUP if configured
            if LOG_GROUP_ID:
                log_text = (
                    "🔓 **#MOD_LOG: USER UNBANNED**\n\n"
                    f"👥 **Chat:** `{event.chat.title}` (`{event.chat_id}`)\n"
                    f"👤 **Target:** `{getattr(target_user, 'first_name', 'User')}` (`{reply.sender_id}`)\n"
                    f"👮 **Admin:** `{getattr(admin_user, 'first_name', 'Admin')}` (`{admin_user.id}`)"
                )
                await event.client.send_message(LOG_GROUP_ID, log_text)
                
        except Exception as e:
            await event.reply(f"❌ Error: `{e}`")