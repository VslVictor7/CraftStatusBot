import discord, os, aiohttp, asyncio
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from mcstatus import JavaServer
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))
MINECRAFT_SERVER_IP = os.getenv('MINECRAFT_SERVER_IP')
MINECRAFT_SERVER_PORT = int(os.getenv('MINECRAFT_SERVER_PORT'))

# Configurando o bot como commands.Bot para usar comandos de barra
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.uptime_start = None  # Armazena o tempo de início do uptime do servidor
        self.activity_log = []  # Armazena o log de atividades

    async def setup_hook(self):
        await self.tree.sync()  # Sincroniza os comandos de barra com o Discord

bot = MyBot()
server = JavaServer.lookup(f"{MINECRAFT_SERVER_IP}:{MINECRAFT_SERVER_PORT}")

async def get_public_ipv4(session):
    try:
        async with session.get("https://api.ipify.org?format=json") as response:
            data = await response.json()
            return data.get("ip")
    except aiohttp.ClientError as e:
        print(f"Erro de Fetching: {e}")
        return None

async def get_server_status():
    try:
        status = await server.async_status()
        players_online = status.players.online
        # Define o início do uptime se o servidor está online pela primeira vez
        if bot.uptime_start is None:
            bot.uptime_start = datetime.utcnow()
        return True, players_online
    except Exception as e:
        print(f"Erro ao obter informações do servidor: {e}")
        bot.uptime_start = None  # Reseta o uptime caso o servidor esteja offline
        return False, 0

async def update_message_periodically(channel, message, session, interval=5):
    last_status = None
    last_ip = None
    last_players_online = None
    while True:
        current_ip = await get_public_ipv4(session)
        server_online, players_online = await get_server_status()
        status_icon = "🟢" if server_online else "🔴"
        status_text = "Online" if server_online else "Offline"
        players_text = (
            "Nenhum" if players_online == 0 else
            f"{players_online} jogador online" if players_online == 1 else
            f"{players_online} jogadores online"
        ) if server_online else "Nenhum"

        # Atualiza a mensagem se houve mudança no estado
        if (current_ip != last_ip or server_online != last_status or
            players_online != last_players_online):
            try:
                embed = discord.Embed(title="Status do Servidor Minecraft", color=0x00ff00 if server_online else 0xff0000)
                embed.add_field(name="🖥️ IP", value=current_ip, inline=False)
                embed.add_field(name="📶 Status", value=f"{status_icon} {status_text}", inline=False)
                embed.add_field(name="👥 Jogadores online", value=players_text, inline=False)

                await message.edit(embed=embed, content="")
                print("Mensagem atualizada.")
                last_ip = current_ip
                last_status = server_online
                last_players_online = players_online
            except discord.DiscordException as e:
                print(f"Erro ao atualizar mensagem: {e}")

        await asyncio.sleep(interval)

# Comando de barra para exibir o uptime
@bot.tree.command(name="uptime", description="Verifica o tempo que o servidor está online")
async def uptime(interaction: discord.Interaction):
    if bot.uptime_start is None:
        await interaction.response.send_message("O servidor está offline no momento, portanto não há tempo de uptime.")
    else:
        uptime_duration = datetime.utcnow() - bot.uptime_start
        hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_message = f"Servidor online há: {hours} horas, {minutes} minutos e {seconds} segundos."
        await interaction.response.send_message(uptime_message)

# Comando para exibir o log de atividades
@bot.tree.command(name="log", description="Exibe o log de atividades do servidor")
async def log(interaction: discord.Interaction):
    if not bot.activity_log:
        await interaction.response.send_message("Não há atividades registradas no log.")
        return

    log_message = "\n".join(bot.activity_log)
    await interaction.response.send_message(f"Atividades registradas:\n{log_message}")

# Evento de inicialização do bot
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
                print(f"Erro de Fetching: {e}")
                await bot.close()
        else:
            print("Canal não detectado.")
            await bot.close()

# Executa o bot com o token
bot.run(TOKEN)