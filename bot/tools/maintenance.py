import discord
import os
import pytz
from datetime import datetime
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.event
async def on_ready():

    bot_name = bot.user.name

    print(f"[BOT] Logado como {bot_name} - {bot.user.id}")

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        message = await channel.fetch_message(MESSAGE_ID)
        print("[BOT STARTED] Atualizando para manutenção...")

        await update_discord_message(message, bot_name)
        print("[BOT OFF] Pronto.")
        await bot.close()

async def update_discord_message(message, bot_name):
        try:
            embed = create_embed(bot_name)
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            current_time = datetime.now(sao_paulo_tz)
            await message.edit(embed=embed, content="")
            print(f"[BOT] Mensagem do servidor atualizada as: {current_time}.")
        except discord.DiscordException as e:
            print(f"[ERROR] Falha ao atualizar mensagem: {e}")

def create_embed(bot_name):
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(sao_paulo_tz)

    embed = discord.Embed(
        title="Status do Servidor Minecraft",
        color=discord.Colour(0xFF7F00),
    )
    embed.add_field(name="🖥️ IP", value="Nenhum", inline=False)
    embed.add_field(name="📶 Status", value="🟠 Manutenção", inline=False)
    embed.add_field(
        name="👥 Jogadores Online",
        value="Nenhum",
        inline=False
    )

    embed.add_field(name="📝 Nomes", value="Nenhum", inline=False)

    embed.add_field(name="🌐 Versão", value="Desconhecido", inline=False)

    embed.timestamp = current_time

    embed.set_footer(
        text=bot_name
    )

    return embed

if __name__ == '__main__':
    bot.run(TOKEN)