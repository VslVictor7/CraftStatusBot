from minecraft import message_manager
import discord, os, aiohttp
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))

bot = message_manager.MyBot()

# Comandos.

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

@bot.tree.command(name="ping", description="Verifica o ping do servidor Minecraft")
async def ping(interaction: discord.Interaction):
    try:
        latency = bot.server.ping()  # Obtém o ping do servidor
        await interaction.response.send_message(f"Ping do servidor é de {latency} ms")
    except Exception as e:
        await interaction.response.send_message(f"Ocorreu um erro ao tentar obter o ping: {e}")

# Rodar o bot.

@bot.event
async def on_ready():

    activity = discord.Activity(type=discord.ActivityType.watching, name="Movimentação do nosso servidor")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    async with aiohttp.ClientSession() as session:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(MESSAGE_ID)
                print("Bot pronto para monitoramento de IP, Servidor e Jogadores.")
                await message_manager.update_message_periodically(channel, message, session)
            except discord.DiscordException as e:
                print(f"Erro ao buscar mensagem: {e}")
                await bot.close()
        else:
            print("Canal não detectado.")
            await bot.close()

bot.run(TOKEN)