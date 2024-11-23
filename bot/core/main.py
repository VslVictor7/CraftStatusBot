import discord
import os
import aiohttp
import time
from scripts.mybot import MyBot
from scripts.message_manager import update_message_periodically
from commands import setup_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))

# Rodar o bot.

bot = MyBot()

async def sync_commands(bot):
    try:
        start_time = time.time()
        await bot.tree.sync()
        end_time = time.time()

        sync_duration = end_time - start_time

        minutes = int(sync_duration // 60)
        seconds = int(sync_duration % 60)

        print(f"[BOT SYNC] Comandos sincronizados globalmente. Feito em {minutes} minutos e {seconds} segundos.")

    except Exception as e:
        print(f"[BOT ERROR] Falha ao sincronizar os comandos: {e}")

@bot.event
async def on_ready():

    print(f"[BOT] Logado como {bot.user.name} - {bot.user.id}")

    bot.loop.create_task(setup_commands(bot))
    bot.loop.create_task(sync_commands(bot))

    activity = discord.Activity(type=discord.ActivityType.watching, name="Movimentação do nosso servidor")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    is_online, uptime_start = await bot.get_server_uptime()
    if is_online:
        bot.uptime_start = uptime_start
        print(f"[BOT] Uptime do servidor iniciado e registrado as: {bot.uptime_start}")
    else:
        print("[BOT ERROR] Não foi possível verificar o uptime do servidor.")

    async with aiohttp.ClientSession() as session:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(MESSAGE_ID)
                print("[BOT STARTED] Pronto para monitoramento de IP, Servidor e Jogadores")
                await update_message_periodically(channel, message, session)
            except discord.DiscordException as e:
                print(f"[BOT ERROR] Erro ao buscar mensagem: {e}")
                await bot.close()
        else:
            print("[BOT ERROR] Canal não detectado.")
            await bot.close()

bot.run(TOKEN)