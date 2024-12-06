import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("PLAYER_EVENT_LOGS"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

async def player_events(bot):

    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não detectado para envio de player events. Saindo da função.")
        return

    processed_lines = set()
    await asyncio.sleep(5)

    while True:
        try:
            with open(LOG_FILE_PATH, "r") as file:
                lines = file.readlines()

            for line in lines:
                if line in processed_lines:
                    continue
                processed_lines.add(line)

                if "joined the game" in line:
                    player_name = extract_player_name(line)
                    if player_name:
                        embed = create_embed(player_name, f"{player_name} entrou no servidor", 0x00ff00)
                        await asyncio.sleep(2)
                        await channel.send(embed=embed)

                elif "left the game" in line:
                    player_name = extract_player_name(line)
                    if player_name:
                        embed = create_embed(player_name, f"{player_name} saiu do servidor", 0xff0000)
                        await asyncio.sleep(2)
                        await channel.send(embed=embed)

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        await asyncio.sleep(10)


def extract_player_name(log_line):
    try:
        # Exemplo: "VictorVsl7 joined the game" ou "VictorVsl7 left the game"
        if "joined the game" in log_line or "left the game" in log_line:
            parts = log_line.split("]:")  # Divide após o primeiro "]:"
            player_action_part = parts[-1].strip()  # Última parte contém o nome do jogador e a ação
            player_name = player_action_part.split(" ")[0] # O nome do jogador é a primeira palavra
            return player_name
    except IndexError:
        return None

def create_embed(player_name, title, color):
    url = f"https://mineskin.eu/helm/{player_name}/30"

    embed = discord.Embed(
        color=color
    )

    embed.set_author(name=title, icon_url=url)

    return embed
