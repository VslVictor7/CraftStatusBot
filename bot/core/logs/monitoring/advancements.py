import discord
from deep_translator import GoogleTranslator

async def process_advancements_messages(log_line, channel):
    try:

        ignore_patterns = [
            "[Rcon]", "[Not Secure]", "Disconnecting VANILLA connection attempt",
            "rejected vanilla connections", "lost connection", "id=<null>", "legacy=false",
            "lost connection: Disconnected", "<init>", "<", ">"
        ]

        if any(pattern in log_line for pattern in ignore_patterns):
            return

        player_name, message, event_name = extract_player_message(log_line)

        if player_name and message and event_name:

            if "has reached the goal" in message:
                await event_translation(channel, player_name, event_name, 0xFFA500, "alcançou um objetivo:")
            elif "has made the advancement" in message:
                await event_translation(channel, player_name, event_name, 0x0000FF, "obteve um avanço:")
            elif "has completed the challenge" in message:
                await event_translation(channel, player_name, event_name, 0x800080, "completou um desafio:")

        return
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


async def event_translation(channel, player_name, event_name, color, action):
    event_translated = GoogleTranslator(source='en', target='pt').translate(event_name)
    await send_player_event(channel, player_name, action, event_name, event_translated, color)


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