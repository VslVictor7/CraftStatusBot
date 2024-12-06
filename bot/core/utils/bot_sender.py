import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} conectado ao Discord!')

    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send('Mensagem placeholder para atualização de campo Embed.')
    else:
        print('Canal não encontrado.')

bot.run(TOKEN)
