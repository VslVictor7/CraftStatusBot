import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = "token com aspas, é uma STR"
CHANNEL_ID = 'id deve ser sem aspas, é um INT'

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} conectado ao Discord!')

    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send('Mensagem placeholder para meu IP.')
    else:
        print('Canal não encontrado.')

# Execute o bot
bot.run(TOKEN)
