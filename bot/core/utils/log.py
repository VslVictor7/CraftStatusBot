import requests
import discord
import time
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = os.getenv("CHANNEL_LOGS")
LOG_FILE_PATH = os.getenv("SERVER_LOGS")


def log_events(bot):

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        log_channel = bot.get_channel(CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"Nova mensagem de {message.author}: {message.content}")

    @bot.event
    async def on_member_join(member):
        log_channel = bot.get_channel(CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"{member} entrou no servidor!")

    @bot.event
    async def on_member_remove(member):
        log_channel = bot.get_channel(CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"{member} saiu do servidor!")