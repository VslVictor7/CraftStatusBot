import asyncio
import os
import discord
from .monitoring.player_chat import process_user_messages
from .monitoring.player_death import process_death_event
from .monitoring.advancements import process_advancements_messages
from .monitoring.mobs_death import process_mobs_death_event
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
    if not os.path.exists(LOG_FILE_PATH):
        print(f"[LOG ERROR] Arquivo de log não encontrado: {LOG_FILE_PATH}")
        return

    webhook = await ensure_webhook(channel)

    await monitor_log_file(webhook, channel)


async def monitor_log_file(webhook, channel):
    try:
        with open(LOG_FILE_PATH, "r") as file:
            file.seek(0, os.SEEK_END)

            while True:
                line = file.readline()
                if not line:
                    await asyncio.sleep(0.1)
                    continue

                await process_line(line, webhook, channel)

    except FileNotFoundError:
        print(f"[LOG ERROR] Arquivo de log não encontrado: {LOG_FILE_PATH}")
    except Exception as e:
        print(f"[LOG ERROR] Erro no monitoramento do arquivo de log: {e}")


async def process_line(line, webhook, channel):
    try:
        tasks = []

        tasks.append(process_death_event(line, channel))
        tasks.append(process_mobs_death_event(line, channel))
        tasks.append(process_advancements_messages(line, channel))
        tasks.append(process_user_messages(webhook, line))

        await asyncio.gather(*tasks)

    except Exception as e:
        print(f"[LOG ERROR] Erro ao processar a linha: {e}")

async def ensure_webhook(channel):
    try:
        webhooks = await channel.webhooks()
        webhook = discord.utils.get(webhooks, name="Minecraft Chat Webhook")
        if webhook is None:
            webhook = await channel.create_webhook(name="Minecraft Chat Webhook")
            print("[BOT INFO] Webhook criado com sucesso.")
        return webhook
    except Exception as e:
        print(f"[BOT ERROR] Erro ao criar o webhook: {e}")
        return None