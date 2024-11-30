import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_TEST_ID"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

previous_lines = []

async def monitor_file(bot):
    """Monitora o arquivo `latest.txt` e envia mensagens quando novos conteúdos são detectados."""
    global previous_lines

    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não detectado.")
        return

    while True:
        try:
            with open(LOG_FILE_PATH, "r") as file:
                lines = file.readlines()

            # Identifica novas linhas adicionadas
            new_lines = lines[len(previous_lines):]
            previous_lines = lines  # Atualiza o estado do arquivo

            for line in new_lines:
                await channel.send(line.strip())
                print(f"[BOT] Enviou nova linha: {line.strip()}")

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        # Intervalo de verificação
        await asyncio.sleep(5)  # Verifica a cada 5 segundos