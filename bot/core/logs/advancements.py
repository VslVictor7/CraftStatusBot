import asyncio
import os
import discord
from googletrans import Translator
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_CHAT_EVENTS_ID"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

async def advancements(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não detectado para envio de conquistas. Saindo da função.")
        return

    server_started = False
    file_position = 0
    last_file_size = os.path.getsize(LOG_FILE_PATH)

    initial_delay = 10
    print(f"[LOG INFO] Aguardando {initial_delay} segundos para começar análise de conquistas...")
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
                    if not server_started and "Done" in line:
                        server_started = True
                        print("[LOG INFO] Servidor iniciado. Iniciando o monitoramento dos eventos dos jogadores.")
                        continue

                    if server_started:
                        await process_user_messages(line, channel)

                    if "Stopping the server" in line:
                        server_started = False
                        print("[LOG INFO] Servidor parado. Parando o monitoramento dos eventos dos jogadores.")

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        await asyncio.sleep(2.5)

async def process_user_messages(log_line, channel):
    translator = Translator()
    try:
        player_name, message, event_name = extract_player_message(log_line)

        if player_name and message and event_name:
            if "has reached the goal" in message:
                event_translated = translator.translate(event_name, src='en', dest='pt').text
                await send_player_event(channel, player_name, "alcançou o objetivo:", event_name, event_translated, discord.Color.orange())

            elif "has made the advancement" in message:
                event_translated = translator.translate(event_name, src='en', dest='pt').text
                await send_player_event(channel, player_name, "obteve o avanço:", event_name, event_translated, discord.Color.blue())

            elif "has completed the challenge" in message:
                event_translated = translator.translate(event_name, src='en', dest='pt').text
                await send_player_event(channel, player_name, "completou o desafio:", event_name, event_translated, discord.Color.purple())

    except Exception as e:
        print(f"Erro ao processar evento de usuários mandando mensagens no discord: {e}")

def extract_player_message(log_line):
    try:
        message_part = log_line.split("]: ")[1]

        player_name_end = message_part.index(" has ")
        player_name = message_part[:player_name_end]

        message = message_part[player_name_end:].split("[")[0].strip()

        event_name_start = message_part.index("[") + 1
        event_name_end = message_part.index("]")
        event_name = message_part[event_name_start:event_name_end].strip()

        return player_name, message, event_name
    except ValueError:
        return None, None, None

async def send_player_event(channel, player_name, event_message, event_name, event_translated, color):
    try:
        embed = discord.Embed(color=color)
        embed.set_author(
            name=f'{player_name} {event_message} {event_name} ({event_translated})',
            icon_url=f"https://mineskin.eu/helm/{player_name}"
        )
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[BOT ERROR] Falha ao enviar evento do jogador como embed: {e}")

async def send_message_as_user(channel, username, message):
    try:
        await channel.send(
            content=message,
            username=username,
            avatar_url=f"https://mineskin.eu/helm/{username}"
        )
    except Exception as e:
        print(f"[BOT ERROR] Falha ao enviar mensagem como usuário: {e}")
