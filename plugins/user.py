from telethon import events

def register(client, **kwargs):
    @client.on(events.NewMessage(pattern=r"^/id$"))
    async def id_handler(event):
        reply = await event.get_reply_message()
        user = reply.sender if reply else event.sender
        await event.reply(f"🆔 **User ID:** `{user.id}`\n💬 **Chat ID:** `{event.chat_id}`")

    @client.on(events.NewMessage(pattern=r"^/userinfo$"))
    async def userinfo_handler(event):
        reply = await event.get_reply_message()
        user = reply.sender if reply else event.sender
        await event.reply(
            f"👤 **User Profile Info:**\n"
            f"• Name: {user.first_name}\n"
            f"• Username: @{user.username if user.username else 'None'}\n"
            f"• ID: `{user.id}`"
        )