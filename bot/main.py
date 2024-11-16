import discord
import os
import aiohttp
import pytz
from minecraft.scripts import message_manager
from aniversario import birthday_checker
from musica import lyrics_finder
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))
FRIENDS_BIRTHDAYS = os.getenv('BIRTHDAYS')
DISCORD_CHANNEL_ID = int(os.getenv('CHANNEL_TEST_ID'))

bot = message_manager.MyBot()

sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
current_time = datetime.now(sao_paulo_tz)

def create_embed(title, description, color):

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.timestamp = current_time

    return embed

@bot.tree.command(name="uptime", description="Mostra o tempo que o servidor está online.")
async def uptime(interaction: discord.Interaction):
    if bot.uptime_start:
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        current_time = datetime.now(sao_paulo_tz)
        uptime_duration = current_time - bot.uptime_start
        hours, remainder = divmod(uptime_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_message = f"O servidor está online há {hours} horas, {minutes} minutos e {seconds} segundos."

        embed = create_embed("Uptime do Servidor", uptime_message, 0x7289DA)

        await interaction.response.send_message(embed=embed)
    else:
        return await interaction.response.send_message("O servidor está offline no momento.", ephemeral=True)


@bot.tree.command(name="ping", description="Verifica o ping do servidor Minecraft")
async def ping(interaction: discord.Interaction):

    try:
        latency = bot.server.ping()
        latency = round(latency, 2)

        latency_text = f"{latency} ms"

        embed = create_embed("Latência do Servidor", latency_text, 0x7289DA)

        await interaction.response.send_message(embed=embed)

    except Exception as e:

        latency_text = f"Erro ao obter latência: {e}"

        embed = create_embed("Latência do Servidor", latency_text, 0x7289DA)

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="letra", description="Busca a letra de uma música no Genius")
async def fetch_lyrics(interaction: discord.Interaction, song_title: str):
    await interaction.response.defer()
    final_title, lyrics = lyrics_finder.get_song_lyrics(song_title)

    if final_title == "Nenhuma música encontrada.":
        await interaction.followup.send(final_title)
        return

    partes_lyricas = lyrics_finder.split_lyrics(lyrics)

    for parte in partes_lyricas:
        embed = create_embed(f"Letra de {final_title}", parte, 0x7289DA)
        await interaction.followup.send(embed=embed)

# Rodar o bot.

@bot.event
async def on_ready():

    activity = discord.Activity(type=discord.ActivityType.watching, name="Movimentação do nosso servidor")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    is_online, uptime_start = await bot.get_server_uptime()
    if is_online:
        bot.uptime_start = uptime_start  # Armazena o horário de início do uptime
        print(f"Uptime do servidor iniciado em: {bot.uptime_start}")
    else:
        print("Servidor offline ou não foi possível verificar o status.")

    async with aiohttp.ClientSession() as session:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(MESSAGE_ID)
                print("Bot pronto para monitoramento de Status, Servidor, Jogadores e Aniversariantes.")
                parsed_birthdays = birthday_checker.parse_birthdays(FRIENDS_BIRTHDAYS)
                bot.loop.create_task(birthday_checker.birthday_check_periodically(bot, parsed_birthdays, DISCORD_CHANNEL_ID))
                print("Lista de aniversariantes analisadas.")
                await message_manager.update_message_periodically(channel, message, session)
            except discord.DiscordException as e:
                print(f"Erro ao buscar mensagem: {e}")
                await bot.close()
        else:
            print("Canal não detectado.")
            await bot.close()

bot.run(TOKEN)