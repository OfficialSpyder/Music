from telethon import events
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights, ChannelParticipantAdmin, ChannelParticipantCreator

try:
    from config import LOG_GROUP_ID
except ImportError:
    LOG_GROUP_ID = None

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/promote(?: (.+))?$"))
    async def promote_handler(event):
        if not event.is_group:
            return await event.reply("⚠️ This command can only be used in groups!")
        
        # Check if the user is admin or owner
        try:
            sender_perms = await event.client.get_permissions(event.chat_id, event.sender_id)
            if not sender_perms.is_admin and not sender_perms.is_creator:
                return await event.reply("❌ **Access Denied:** Only group admins or owners can use this command.")
        except Exception:
            return await event.reply("⚠️ Failed to verify administrative permissions.")

        reply = await event.get_reply_message()
        user = reply.sender_id if reply else None
        if not user:
            return await event.reply("⚠️ Reply to a user's message to promote them to Admin.")
        
        try:
            target_user = await event.client.get_entity(user)
            admin_user = await event.get_sender()

            rights = ChatAdminRights(
                change_info=True, post_messages=True, edit_messages=True,
                delete_messages=True, ban_users=True, invite_users=True,
                pin_messages=True, manage_call=True
            )
            await client(EditAdminRequest(event.chat_id, user, rights, rank="Admin"))
            await event.reply("✅ **User successfully promoted to Administrator with full privileges!**")
            
            # Send log to LOG_GROUP if configured
            if LOG_GROUP_ID:
                log_text = (
                    "👑 **#MOD_LOG: USER PROMOTED**\n\n"
                    f"👥 **Chat:** `{event.chat.title}` (`{event.chat_id}`)\n"
                    f"👤 **Target:** `{getattr(target_user, 'first_name', 'User')}` (`{user}`)\n"
                    f"👮 **Admin:** `{getattr(admin_user, 'first_name', 'Admin')}` (`{admin_user.id}`)"
                )
                await event.client.send_message(LOG_GROUP_ID, log_text)

        except Exception as e:
            await event.reply(f"❌ Failed to promote: `{e}`")

    @client.on(events.NewMessage(pattern=r"^/demote$"))
    async def demote_handler(event):
        if not event.is_group:
            return
        
        # Check if the user is admin or owner
        try:
            sender_perms = await event.client.get_permissions(event.chat_id, event.sender_id)
            if not sender_perms.is_admin and not sender_perms.is_creator:
                return await event.reply("❌ **Access Denied:** Only group admins or owners can use this command.")
        except Exception:
            return await event.reply("⚠️ Failed to verify administrative permissions.")

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ Reply to a user to demote them.")
        
        try:
            target_user = await event.client.get_entity(reply.sender_id)
            admin_user = await event.get_sender()

            no_rights = ChatAdminRights(False, False, False, False, False, False, False, False, False)
            await client(EditAdminRequest(event.chat_id, reply.sender_id, no_rights, rank="Member"))
            await event.reply("✅ **Administrator privileges revoked successfully.**")
            
            # Send log to LOG_GROUP if configured
            if LOG_GROUP_ID:
                log_text = (
                    "🔻 **#MOD_LOG: USER DEMOTED**\n\n"
                    f"👥 **Chat:** `{event.chat.title}` (`{event.chat_id}`)\n"
                    f"👤 **Target:** `{getattr(target_user, 'first_name', 'User')}` (`{reply.sender_id}`)\n"
                    f"👮 **Admin:** `{getattr(admin_user, 'first_name', 'Admin')}` (`{admin_user.id}`)"
                )
                await event.client.send_message(LOG_GROUP_ID, log_text)

        except Exception as e:
            await event.reply(f"❌ Failed to demote: `{e}`")