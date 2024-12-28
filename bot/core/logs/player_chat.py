async def process_user_messages(webhook, log_line):
    try:
        if "<" not in log_line or ">" not in log_line:
            return
        if "[Not Secure]" in log_line or "[Rcon]" in log_line:
            return
        if "Disconnecting VANILLA connection attempt" in log_line or "rejected vanilla connections" in log_line:
            return

        ignore_patterns = [
            "lost connection",
            "id=<null>",
            "legacy=false",
            "lost connection: Disconnected",
            "<init>"
        ]

        if any(pattern in log_line for pattern in ignore_patterns):
            return

        player_name, message = extract_player_message(log_line)

        if player_name and message:
            await send_message_as_user(webhook, player_name, message)
    except Exception as e:
        print(f"Erro ao processar evento de usuários mandando mensagens no discord: {e}")


async def send_message_as_user(webhook, username, message):
    try:
        await webhook.send(
            content=message,
            username=username,
            avatar_url=f"https://mineskin.eu/helm/{username}"
        )
    except Exception as e:
        print(f"[BOT ERROR] Falha ao enviar mensagem como usuário: {e}")

def extract_player_message(log_line):
    try:
        start = log_line.index("<") + 1
        end = log_line.index(">")
        player_name = log_line[start:end].strip()
        message = log_line[end + 1:].strip()
        return player_name, message
    except ValueError as e:
        print(f"[BOT] Erro ao extrair nome do jogador e mensagem: {e}")
        return None, None