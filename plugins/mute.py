from telethon import events

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/mute$"))
    async def mute_handler(event):
        if not event.is_group: return
        reply = await event.get_reply_message()
        if not reply: return await event.reply("⚠️ Reply to user to mute.")
        try:
            await event.client.edit_permissions(event.chat_id, reply.sender_id, send_messages=False)
            await event.reply("🔇 **User has been muted successfully.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{e}`")

    @client.on(events.NewMessage(pattern=r"^/unmute$"))
    async def unmute_handler(event):
        if not event.is_group: return
        reply = await event.get_reply_message()
        if not reply: return await event.reply("⚠️ Reply to user to unmute.")
        try:
            await event.client.edit_permissions(event.chat_id, reply.sender_id, send_messages=True)
            await event.reply("🔊 **User mute has been lifted.**")
        except Exception as e:
            await event.reply(f"❌ Error: `{e}`")