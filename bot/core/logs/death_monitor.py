import re
import os
import discord
import json

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

async def process_death_event(log_line, channel):
    try:
        for death_pattern, translated_message in death_messages.items():
            search_pattern = death_pattern.replace("{player}", "(?P<player>\\S+)")

            if "{entity}" in search_pattern:
                search_pattern = search_pattern.replace("{entity}", "(?P<entity>\\S+)")
            if "{item}" in search_pattern:
                search_pattern = search_pattern.replace("{item}", "(?P<item>.+?)")

            match = re.search(search_pattern, log_line)
            if match:
                player = match.group("player")
                raw_entity = match.groupdict().get("entity") or "desconhecido"
                entity = mobs.get(raw_entity, raw_entity)
                item = match.groupdict().get("item") or "desconhecido"

                translated = translated_message
                translated = translated.replace("{entity}", entity)
                translated = translated.replace("{item}", item)

                await send_player_event(channel, player, translated, 0x000000)
                return
    except Exception as e:
        print(f"[BOT ERROR] Erro ao processar evento de morte: {e}")

async def send_player_event(channel, player_name, event_message, color):
    try:
        embed = discord.Embed(color=color)
        embed.set_author(
            name=f"{player_name} {event_message}",
            icon_url=f"https://mineskin.eu/helm/{player_name}"
        )
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[BOT ERROR] Erro ao enviar evento de morte: {e}")
