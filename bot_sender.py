import discord
from discord.ext import commands

TOKEN = ''  # Insira seu token aqui
CHANNEL_ID = ''  # Insira o ID do canal aqui

# Criação do bot com intents
intents = discord.Intents.default()
intents.messages = True  # Permite que o bot leia mensagens

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} conectado ao Discord!')

    # Obtém o canal pelo ID
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        # Envia a mensagem
        await channel.send('Mensagem placeholder para meu IP.')
    else:
        print('Canal não encontrado.')

# Execute o bot
bot.run(TOKEN)
