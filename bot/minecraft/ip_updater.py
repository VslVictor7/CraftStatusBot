import discord, os, aiohttp, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from mcstatus import JavaServer
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))
MINECRAFT_SERVER_IP = os.getenv('MINECRAFT_SERVER_IP')
MINECRAFT_SERVER_PORT = int(os.getenv('MINECRAFT_SERVER_PORT'))

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

        # Obter nomes dos jogadores online, se disponíveis
        player_names = [player.name for player in status.players.sample] if status.players.sample else []

        return True, status.players.online, status.version.name, player_names
    except:
        bot.uptime_start = None
        return False, 0, "Desconhecido", []


def create_embed(ip, server_online, players_online, version, player_names):
    embed = discord.Embed(
        title="Status do Servidor Minecraft",
        color=0x00ff00 if server_online else 0xff0000
    )
    embed.add_field(name="🖥️ IP", value=ip or "N/A", inline=False)
    embed.add_field(name="📶 Status", value="🟢 Online" if server_online else "🔴 Offline", inline=False)
    embed.add_field(name="👥 Jogadores Online", value=f"{players_online} jogador{'es' if players_online != 1 else ''}" if server_online else "Nenhum", inline=False)

    if player_names:
        embed.add_field(name="📝 Nomes", value=", ".join(player_names), inline=False)
    else:
        embed.add_field(name="📝 Nomes", value="Nenhum", inline=False)

    embed.add_field(name="🌐 Versão", value=version, inline=False)

    return embed

async def update_message_periodically(channel, message, session, interval=3):
    last_status, last_ip, last_players_online, last_version, last_player_names = None, None, None, None, None

    while True:
        current_ip = await get_public_ipv4(session)
        server_online, players_online, version, player_names = await get_server_status(bot)

        # Verificar se nenhum nome contém "Anonymous Player"
        if "Anonymous Player" not in player_names:
            # Atualizar mensagem apenas se houver mudanças
            if (current_ip != last_ip or server_online != last_status or players_online != last_players_online
                or version != last_version or player_names != last_player_names):

                # Criar embed com a lista atualizada de jogadores e outras informações
                embed = create_embed(current_ip, server_online, players_online, version, player_names)
                try:
                    await message.edit(embed=embed, content="")
                    print("Mensagem atualizada.")
                except discord.DiscordException as e:
                    print(f"Erro ao atualizar mensagem: {e}")

                # Atualizar o estado anterior
                last_ip, last_status, last_players_online, last_version, last_player_names = (
                    current_ip, server_online, players_online, version, player_names
                )

        # Aguardar intervalo antes da próxima atualização
        await asyncio.sleep(interval)

@bot.tree.command(name="uptime", description="Verifica o tempo que o servidor está online")
async def uptime(interaction: discord.Interaction):
    if bot.uptime_start:
        uptime_duration = datetime.utcnow() - bot.uptime_start
        hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_message = f"Servidor online há: {hours} horas, {minutes} minutos e {seconds} segundos."
        await interaction.response.send_message(uptime_message)
    else:
        await interaction.response.send_message("O servidor está offline no momento.")

@bot.event
async def on_ready():
    async with aiohttp.ClientSession() as session:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(MESSAGE_ID)
                print("Bot pronto para monitoramento de IP, Servidor e Jogadores.")
                await update_message_periodically(channel, message, session)
            except discord.DiscordException as e:
                print(f"Erro ao buscar mensagem: {e}")
                await bot.close()
        else:
            print("Canal não detectado.")
            await bot.close()

bot.run(TOKEN)