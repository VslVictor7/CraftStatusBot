import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_LOGS"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

def extract_message(log_line):
    """Extrai a mensagem enviada por um jogador da linha de log."""
    try:
        if ">: <" in log_line:  # Verifica se a linha contém uma mensagem enviada
            parts = log_line.split(">:")  # Divide após ">:"
            message_part = parts[-1].strip()  # Última parte contém a mensagem
            print(message_part)
            return message_part
    except IndexError:
        return None

async def message_events(bot):

    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não detectado.")
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

                # Verifica se a linha contém uma mensagem no formato "<Jogador> mensagem"
                if ">: <" in line:
                    message = extract_message(line)
                    print(message)
                    if message:
                        print(message)
                        embed = discord.Embed(
                            description=message,
                            color=0x3498db  # Cor para representar uma mensagem
                        )
                        await asyncio.sleep(2)
                        await channel.send(embed=embed)

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        await asyncio.sleep(10)