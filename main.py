import os
import asyncio
import importlib
import logging
from telethon import TelegramClient
from pytgcalls import PyTgCalls
from doctor import BotDoctor
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGGER_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TgMusicBot")

QUEUES = {}
VQUEUES = {}

async def main():
    logger.info("Initializing Modular Plugin Core...")

    userbot = TelegramClient("user_session", API_ID, API_HASH)
    pytgcalls = PyTgCalls(userbot)
    bot = TelegramClient('bot_session', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)

    doctor = BotDoctor(bot, LOGGER_ID)

    # --- DYNAMIC PLUGIN LOADER ---
    plugin_dir = "plugins"
    if os.path.exists(plugin_dir):
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"plugins.{filename[:-3]}"
                try:
                    mod = importlib.import_module(module_name)
                    if hasattr(mod, "register"):
                        mod.register(
                            client=bot,
                            userbot=userbot,
                            pytgcalls=pytgcalls,
                            QUEUES=QUEUES,
                            VQUEUES=VQUEUES
                        )
                        logger.info(f"Loaded Plugin ➱ {filename}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {filename}: {e}")

    await userbot.start()
    await pytgcalls.start()
    logger.info("Master Music Bot running with all advanced plugins successfully!")

    if LOGGER_ID:
        try:
            await bot.send_message(LOGGER_ID, "🟢 **Master Music Bot (Modular Plugin Architecture) Online!**")
        except Exception:
            pass

    await asyncio.gather(
        userbot.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped gracefully.")