import re
import asyncio
import os
import discord
from dotenv import load_dotenv
import json

load_dotenv()

CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_CHAT_EVENTS_ID"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

def load_json(file_name):
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'json', file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError as e:
        print(f"[BOT ERROR] Arquivo não encontrado: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"[BOT ERROR] Erro ao decodificar o arquivo: {e}")
        return {}

death_messages = load_json('deaths.json')
mobs = load_json('mobs.json')

async def monitor_deaths(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não encontrado para envio de eventos de morte.")
        return

    file_position = 0
    last_file_size = os.path.getsize(LOG_FILE_PATH)

    initial_delay = 10
    print(f"[LOG INFO] Aguardando {initial_delay} segundos para começar análise de eventos de morte...")
    await asyncio.sleep(initial_delay)

    while True:
        try:
            with open(LOG_FILE_PATH, "r") as file:
                current_file_size = os.path.getsize(LOG_FILE_PATH)
                if current_file_size < last_file_size:
                    print("[LOG INFO] Arquivo de log reescrito. Resetando a posição.")
                    file_position = 0

                last_file_size = current_file_size

                file.seek(file_position)
                lines = file.readlines()
                file_position = file.tell()

                for line in lines:
                    await process_death_event(line, channel)

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        await asyncio.sleep(2.5)


async def process_death_event(log_line, channel):
    try:
        for death_pattern, translated_message in death_messages.items():
            # Preparar o padrão de busca com regex
            search_pattern = death_pattern.replace("{player}", "(?P<player>\\S+)")

            # Substituir {entity} e {item} com grupos de captura, se existirem
            if "{entity}" in search_pattern:
                search_pattern = search_pattern.replace("{entity}", "(?P<entity>\\S+)")
            if "{item}" in search_pattern:
                search_pattern = search_pattern.replace("{item}", "(?P<item>.+?)")

            # Buscar correspondência
            match = re.search(search_pattern, log_line)
            if match:
                player = match.group("player")
                raw_entity = match.groupdict().get("entity") or "desconhecido"
                entity = mobs.get(raw_entity, raw_entity)
                item = match.groupdict().get("item") or "desconhecido"

                # Traduzir mensagem
                translated = translated_message
                translated = translated.replace("{entity}", entity)
                print(translated)
                translated = translated.replace("{item}", item)

                # Enviar mensagem no Discord
                await send_player_event(channel, player, translated, 0x000000)
                return
    except Exception as e:
        print(f"[BOT ERROR] Erro ao processar evento de morte: {e}")
async def send_player_event(channel, player_name, event_message, color):
    embed = discord.Embed(color=color)
    embed.set_author(
        name=f"{player_name} {event_message}",
        icon_url=f"https://mineskin.eu/helm/{player_name}"
    )
    await channel.send(embed=embed)
