import asyncio
import threading
import os
import discord
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .player_chat import process_user_messages
from .death_monitor import process_death_event
from .advancements import process_advancements_messages
from .mobs_death_monitor import process_mobs_death_event
from dotenv import load_dotenv

load_dotenv()

LOG_FILE_PATH = os.getenv("SERVER_LOGS")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_CHAT_EVENTS_ID"))

async def log_handling(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não encontrado para envio de eventos de morte.")
        return

    webhook = await ensure_webhook(channel)

    start_watchdog(webhook, channel)


def start_watchdog(webhook, channel):
    loop = asyncio.get_event_loop()

    handlers = [
        DeathLogHandler(loop, channel),
        MobDeathLogHandler(loop, channel),
        AdvancementLogHandler(loop, channel),
        UserMessageLogHandler(loop, channel, webhook),
    ]

    observer = Observer()
    for handler in handlers:
        observer.schedule(handler, path=(LOG_FILE_PATH), recursive=False)

    observer.start()
    print("[LOG INFO] Monitorando o arquivo de log com múltiplos handlers...")
    observer_thread = threading.Thread(target=observer.join)
    observer_thread.start()

class BaseLogHandler(FileSystemEventHandler):
    def __init__(self, loop, channel):
        self.loop = loop
        self.channel = channel
        self.file_position = 0

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            if not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.process_changes(), self.loop)
            else:
                print("[LOG ERROR] Tentativa de uso do loop de eventos fechado.")

    async def process_changes(self):
        try:
            with open(LOG_FILE_PATH, "r") as file:
                file.seek(self.file_position)
                lines = file.readlines()
                self.file_position = file.tell()

                for line in lines:
                    await self.process_event(line)
        except Exception as e:
            print(f"[LOG ERROR] Erro ao processar arquivo de log: {e}")

    async def process_event(self, line):
        raise NotImplementedError("Esta classe base não implementa o processamento de eventos.")

class DeathLogHandler(BaseLogHandler):
    async def process_event(self, line):
        try:
            await process_death_event(line, self.channel)
        except Exception as e:
            print(f"[LOG ERROR] Erro no processamento de eventos de morte: {e}")

class MobDeathLogHandler(BaseLogHandler):
    async def process_event(self, line):
        try:
            await process_mobs_death_event(line, self.channel)
        except Exception as e:
            print(f"[LOG ERROR] Erro no processamento de eventos de morte: {e}")

class UserMessageLogHandler(BaseLogHandler):
    def __init__(self, loop, channel, webhook):
        super().__init__(loop, channel)
        self.webhook = webhook

    async def process_event(self, line):
        try:
            await process_user_messages(self.webhook, line)
        except Exception as e:
            print(f"[LOG ERROR] Erro no processamento de mensagens de usuários: {e}")

class AdvancementLogHandler(BaseLogHandler):
    async def process_event(self, line):
        try:
            await process_advancements_messages(line, self.channel)
        except Exception as e:
            print(f"[LOG ERROR] Erro no processamento de conquistas: {e}")


async def ensure_webhook(channel):
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="Minecraft Chat Webhook")
    if webhook is None:
        webhook = await channel.create_webhook(name="Minecraft Chat Webhook")
        print("[BOT INFO] Webhook criado com sucesso.")
    return webhook