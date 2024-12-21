import asyncio
import discord
from dotenv import load_dotenv
from mcrcon import MCRcon
import os

load_dotenv()

DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_CHAT_EVENTS_ID"))
RCON_HOST = os.getenv("RCON_HOST")
RCON_PASSWORD = os.getenv("RCON_PASSWORD")

previous_players = set()

async def start_player_events(bot):
        await bot.wait_until_ready()
        channel = bot.get_channel(DISCORD_CHANNEL_ID)

        if not channel:
            print("[BOT ERROR] Canal do Discord não encontrado.")
            return

        print("[BOT INFO] Iniciando monitoramento do servidor Minecraft...")

        asyncio.create_task(check_player_events(channel))

async def check_player_events(channel):
    global previous_players
    while True:
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
                while True:
                    response = mcr.command("list")
                    players = extract_player_list(response)

                    joined = players - previous_players
                    for player in joined:
                        await send_player_event(channel, player, "entrou no servidor", 0x00FF00)

                    left = previous_players - players
                    for player in left:
                        await send_player_event(channel, player, "saiu do servidor", 0xFF0000)

                    previous_players = players
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"[BOT ERROR] Erro ao verificar eventos de jogadores: {e}")
            interval = 60
            print(f"[BOT INFO] Tentando reconectar ao servidor com RCON em {interval} segundos...")
            await asyncio.sleep(60)

async def send_player_event(channel, player_name, event_message, color):
        embed = discord.Embed(color=color)
        embed.set_author(
            name=f"{player_name} {event_message}",
            icon_url=f"https://mineskin.eu/helm/{player_name}"
        )
        await channel.send(embed=embed)

def extract_player_list(response):
        try:
            if ":" in response:
                players_part = response.split(":")[1].strip()
                if players_part:
                    return set(players_part.split(", "))
            return set()
        except Exception:
            return set()
