import os
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()

RCON_HOST = os.getenv("RCON_HOST")
RCON_PORT = int(os.getenv("RCON_PORT"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_CHAT_EVENTS_ID"))


async def message_on_server(bot):

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.channel.id != DISCORD_CHANNEL_ID:
            return

        username = message.author.name
        content = message.content

        minecraft_message = f"<{username}> {content}"

        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
                mcr.command(f"say {minecraft_message}")
            print(f"[MINECRAFT MESSAGE SENT] {minecraft_message}")
        except Exception as e:
            print(f"[BOT ERROR] Falha ao enviar mensagem para o servidor Minecraft: {e}")