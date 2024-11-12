import discord, os, aiohttp
from minecraft.scripts import message_manager
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))

bot = message_manager.MyBot()

# Comandos.

@bot.tree.command(name="uptime", description="Mostra o tempo que o servidor está online.")
async def uptime(interaction: discord.Interaction):
    if not await message_manager.get_server_status(bot) or not bot.uptime_start:
        return await interaction.response.send_message("O servidor está offline no momento.", ephemeral=True)

    uptime_duration = datetime.utcnow() - bot.uptime_start

    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="Uptime do Servidor",
        description=f"O servidor está online há {hours} horas, {minutes} minutos e {seconds} segundos.",
        color=0x7289DA
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ping", description="Verifica o ping do servidor Minecraft")
async def ping(interaction: discord.Interaction):
    try:
        latency = bot.server.ping()

        latency = round(latency, 2)

        embed = discord.Embed(
            title="Latência do Servidor",
            description=f"{latency} ms",
            color=0x7289DA
        )

        await interaction.response.send_message(embed=embed)

    except Exception as e:

        embed = discord.Embed(
            title="Latência do Servidor",
            description=f"Erro ao obter latência: {e}",
            color=0x7289DA
        )
        await interaction.response.send_message(embed=embed)

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