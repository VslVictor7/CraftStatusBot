import discord
import aiohttp
import asyncio
import socket
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))
MINECRAFT_SERVER_IP = os.getenv('MINECRAFT_SERVER_IP')
MINECRAFT_SERVER_PORT = int(os.getenv('MINECRAFT_SERVER_PORT'))

client = discord.Client(intents=discord.Intents.default())

async def get_public_ipv4(session):
    try:
        async with session.get("https://api.ipify.org?format=json") as response:
            data = await response.json()
            return data.get("ip")
    except aiohttp.ClientError as e:
        print(f"Erro de Fetching: {e}")
        return None

async def is_server_online():
    try:
        with socket.create_connection((MINECRAFT_SERVER_IP, MINECRAFT_SERVER_PORT), timeout=5):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

async def update_message_periodically(channel, message, session, interval=5):
    last_status = None
    last_ip = None
    while True:
        current_ip = await get_public_ipv4(session)
        server_status = await is_server_online()

        status_icon = "🟢" if server_status else "🔴"
        status_text = "Online" if server_status else "Offline"

        if current_ip != last_ip or server_status != last_status:
            try:
                await message.edit(content=f"IP: {current_ip}  |  Status: {status_icon} {status_text}")
                print("Mensagem atualizada.")
                last_ip = current_ip
                last_status = server_status
            except discord.DiscordException as e:
                print(f"Erro ao atualizar mensagem: {e}")

        await asyncio.sleep(interval)

@client.event
async def on_ready():
    async with aiohttp.ClientSession() as session:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(MESSAGE_ID)
                print("Bot pronto para monitoramento de IP e Servidor.")
                await update_message_periodically(channel, message, session)
            except discord.DiscordException as e:
                print(f"Erro de Fetching: {e}")
                await client.close()
        else:
            print("Canal não detectado.")
            await client.close()

client.run(TOKEN)
