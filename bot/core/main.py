import discord
import os
import aiohttp
from scripts.mybot import MyBot
from scripts.message_manager import update_message_periodically
from utils.database import create_server_data
from utils.log import monitor_file
from utils.player_events import player_events
from commands import setup_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))

# Rodar o bot.

bot = MyBot()

@bot.event
async def on_ready():

    print(f"[BOT] Logado como {bot.user.name} - {bot.user.id}")

    bot.loop.create_task(setup_commands(bot))
    bot.loop.create_task(bot.sync_commands())

    activity = discord.Activity(type=discord.ActivityType.watching, name="Movimentação do nosso servidor")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    is_online, uptime_start = await bot.get_server_uptime()
    if is_online:
        bot.uptime_start = uptime_start
        print(f"[BOT] Uptime do servidor iniciado e registrado as: {bot.uptime_start}")
    else:
        print("[BOT ERROR] Não foi possível verificar o uptime do servidor.")

    create_server_data()

    async with aiohttp.ClientSession() as session:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(MESSAGE_ID)
                print("[BOT STARTED] Pronto para monitoramento de IP, Servidor e Jogadores.")

                bot.loop.create_task(monitor_file(bot))
                bot.loop.create_task(player_events(bot))

                await update_message_periodically(channel, message, session)

            except discord.DiscordException as e:
                print(f"[BOT ERROR] Erro ao buscar mensagem: {e}")
                await bot.close()
        else:
            print("[BOT ERROR] Canal não detectado.")
            await bot.close()

bot.run(TOKEN)