import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_CHAT_EVENTS_ID"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

async def player_events(bot):

    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não detectado para envio de player events. Saindo da função.")
        return

    webhook = await ensure_webhook(channel)

    server_started = False
    file_position = 0
    last_file_size = os.path.getsize(LOG_FILE_PATH)

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
                        await process_player_events(line, channel, webhook)

                    if "Stopping the server" in line:
                        server_started = False
                        print("[LOG INFO] Servidor parado. Parando o monitoramento dos eventos dos jogadores.")

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        await asyncio.sleep(3)


async def ensure_webhook(channel):
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="Minecraft Chat Webhook")
    if webhook is None:
        webhook = await channel.create_webhook(name="Minecraft Chat Webhook")
        print("[BOT INFO] Webhook criado com sucesso.")
    return webhook

async def process_player_events(log_line, channel, webhook):
    event_map = {
        "joined the game": ("entrou no servidor", 0x00ff00),
        "left the game": ("saiu do servidor", 0xff0000),
    }

    try:
        for event, (message, color) in event_map.items():
            if event in log_line:
                player_name = extract_player_name(log_line)

                if not player_name:
                    raise ValueError("Falha ao extrair o nome do jogador no LOG.")

                embed = create_embed(player_name, f"{player_name} {message}", color)
                await channel.send(embed=embed)
                return

        if "<" in log_line and ">" in log_line:
            player_name, message = extract_player_message(log_line)
            if player_name and message:
                if "[Not Secure]" not in log_line and "[Rcon]" not in log_line:
                  await send_message_as_user(webhook, player_name, message)
    except Exception as e:
        error_message = f"Erro ao processar evento de jogadores no LOG: {str(e)}"
        await channel.send(error_message)

def extract_player_name(log_line):
    try:
        parts = log_line.split("]:")
        player_action_part = parts[-1].strip()
        player_name = player_action_part.split(" ")[0]
        return player_name
    except IndexError:
        return None

def extract_player_message(log_line):
    try:
        start = log_line.index("<") + 1
        end = log_line.index(">")
        player_name = log_line[start:end].strip()
        message = log_line[end + 1:].strip()
        return player_name, message
    except ValueError:
        return None, None

async def send_message_as_user(webhook, username, message):
    try:
        await webhook.send(
            content=message,
            username=username,
            avatar_url=f"https://mineskin.eu/helm/{username}/30"
        )
    except Exception as e:
        print(f"[BOT ERROR] Falha ao enviar mensagem como usuário: {e}")

def create_embed(player_name, title, color):
    url = f"https://mineskin.eu/helm/{player_name}/30"

    embed = discord.Embed(
        color=color
    )

    embed.set_author(name=title, icon_url=url)

    return embed