import discord, os, asyncio
from . import database
from discord.ext import commands
from dotenv import load_dotenv
from mcstatus import JavaServer
from datetime import datetime

load_dotenv()

MINECRAFT_SERVER_IP = os.getenv('MINECRAFT_SERVER_IP')
MINECRAFT_SERVER_PORT = os.getenv('MINECRAFT_SERVER_PORT')

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.uptime_start = None
        self.server = JavaServer.lookup(f"{MINECRAFT_SERVER_IP}:{MINECRAFT_SERVER_PORT}")

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

async def get_public_ipv4(session):
    async with session.get("https://api.ipify.org?format=json") as response:
        return (await response.json()).get("ip")

async def get_server_status(bot):
    try:
        status = await bot.server.async_status()
        bot.uptime_start = bot.uptime_start or datetime.utcnow()

        player_names = [player.name for player in status.players.sample] if status.players.sample else []

        return True, status.players.online, status.version.name, player_names
    except:
        bot.uptime_start = None
        return False, 0, "Desconhecido", []


def create_embed(ip, server_online, players_online, version, player_names):

    player_names_sorted = sorted(player_names)

    embed = discord.Embed(
        title="Status do Servidor Minecraft",
        color=0x00ff00 if server_online else 0xff0000
    )
    embed.add_field(name="🖥️ IP", value=ip if server_online else "Nenhum", inline=False)
    embed.add_field(name="📶 Status", value="🟢 Online" if server_online else "🔴 Offline", inline=False)
    embed.add_field(
        name="👥 Jogadores Online",
        value="Nenhum" if players_online == 0 else f"{players_online} jogador{'es' if players_online != 1 else ''}",
        inline=False
    )

    if player_names:
        embed.add_field(name="📝 Nomes", value=", ".join(player_names_sorted), inline=False)
    else:
        embed.add_field(name="📝 Nomes", value="Nenhum", inline=False)

    embed.add_field(name="🌐 Versão", value=version, inline=False)

    return embed

async def update_message_periodically(channel, message, session, interval=3):

    def get_left_players(player_names):
        if last_player_names:
            left_players = set(last_player_names) - set(player_names)
            return left_players
        else:
            left_players = set()
            return left_players

    def update_last_state(current_ip, server_online, players_online, version, player_names):
        return current_ip, server_online, players_online, version, player_names

    def update_database(player_name, server_online, players_online, player_left=None):
        if player_left:
            for player in player_left:
                database.insert_server_data(player_name, server_online, players_online, player_left=player)
        else:
            database.insert_server_data(player_name, server_online, players_online)

    async def handle_message_update(message, embed):
        try:
            await message.edit(embed=embed, content="")
            print("Mensagem atualizada.")
        except discord.DiscordException as e:
            print(f"Erro ao atualizar mensagem: {e}")

    last_status, last_ip, last_players_online, last_version, last_player_names = None, None, None, None, None

    while True:

        current_ip = await get_public_ipv4(session)
        server_online, players_online, version, player_names = await get_server_status(bot)

        left_players = get_left_players(player_names)

        if "Anonymous Player" not in player_names:

            player_name = player_names[0] if player_names else None

            if (current_ip != last_ip or server_online != last_status or players_online != last_players_online
                or version != last_version or player_names != last_player_names):

                # Atualizar banco de dados.
                update_database(player_name, server_online, players_online, left_players)

                # Criar embed com conteúdo.
                embed = create_embed(current_ip, server_online, players_online, version, player_names)

                # Atualizar mensagem.
                await handle_message_update(message, embed)

                # Atualizar último estado.

                last_ip, last_status, last_players_online, last_version, last_player_names = update_last_state(
                    current_ip, server_online, players_online, version, player_names
                )

        await asyncio.sleep(interval)