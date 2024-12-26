import discord
from googletrans import Translator

async def process_advancements_messages(log_line, channel):
    translator = Translator()
    try:
        player_name, message, event_name = extract_player_message(log_line)

        if player_name and message and event_name:
            if "has reached the goal" in message:
                event_translated = translator.translate(event_name, src='en', dest='pt').text
                await send_player_event(channel, player_name, "alcançou o objetivo:", event_name, event_translated, 0xFFA500)

            elif "has made the advancement" in message:
                event_translated = translator.translate(event_name, src='en', dest='pt').text
                await send_player_event(channel, player_name, "obteve o avanço:", event_name, event_translated, 0x0000FF)

            elif "has completed the challenge" in message:
                event_translated = translator.translate(event_name, src='en', dest='pt').text
                await send_player_event(channel, player_name, "completou o desafio:", event_name, event_translated, 0x800080)

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
