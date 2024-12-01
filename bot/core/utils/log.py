import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_TEST_ID"))
LOG_FILE_PATH = os.getenv("SERVER_LOGS")

previous_lines = []

async def monitor_file(bot):
    """Monitora o arquivo `latest.txt` e envia mensagens formatadas como uma caixa de código no Discord."""
    global previous_lines

    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("[BOT ERROR] Canal não detectado.")
        return

    # Timer inicial antes de começar o monitoramento
    initial_delay = 10  # Aguarda 10 segundos antes de iniciar
    print(f"[BOT] Aguardando {initial_delay} segundos para enviar logs do servidor...")
    await asyncio.sleep(initial_delay)

    while True:
        try:
            with open(LOG_FILE_PATH, "r") as file:
                lines = file.readlines()

            # Identifica novas linhas adicionadas
            new_lines = lines[len(previous_lines):]
            previous_lines = lines  # Atualiza o estado do arquivo

            if new_lines:
                # Junta as novas linhas em uma string e divide se necessário
                formatted_message = "".join(new_lines)
                code_block = "```\n"  # Cabeçalho para a formatação de código
                footer = "```"  # Rodapé para a formatação de código

                # Quebra o conteúdo em blocos menores para respeitar o limite de 2000 caracteres
                max_length = 2000 - len(code_block) - len(footer)
                chunks = [formatted_message[i:i + max_length] for i in range(0, len(formatted_message), max_length)]

                for chunk in chunks:
                    await channel.send(f"{code_block}{chunk}{footer}")
                    print(f"[BOT] Enviou um chunk de mensagens.")

        except FileNotFoundError:
            print(f"[BOT ERROR] Arquivo '{LOG_FILE_PATH}' não encontrado.")
        except Exception as e:
            print(f"[BOT ERROR] Erro ao monitorar o arquivo: {e}")

        # Intervalo de verificação
        await asyncio.sleep(5)  # Verifica a cada 5 segundos