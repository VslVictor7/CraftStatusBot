import discord
import os
import pytz
import time
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from mcstatus import JavaServer
from datetime import datetime

load_dotenv()

IP = os.getenv('MINECRAFT_SERVER')

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.uptime_start = None
        self.server = JavaServer(IP,JavaServer.DEFAULT_PORT)

    async def get_server_uptime(self):
        try:
            status = self.server.status()
            if status:
                if self.uptime_start is None:
                    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
                    self.uptime_start = datetime.now(sao_paulo_tz)
                return True, self.uptime_start
            else:
                return False, 0
        except Exception as e:
            print(f"Erro ao tentar acessar o servidor: {e}")
            return False, 0

    async def sync_commands(self):
        try:
            await self.tree.sync()
            print("[BOT SYNC] Comandos sincronizados globalmente.")

        except Exception as e:
            print(f"[BOT ERROR] Falha ao sincronizar os comandos: {e}")
        except discord.errors.HTTPException as e:
            if e.code == 429:
                retry_after = e.retry_after
                print(f"[BOT ERROR] Rate limitado. Tentando novamente em  {retry_after} segundos.")
                await asyncio.sleep(retry_after)
            else:
                print(f"[BOT ERROR] Falha ao sincronizar os comandos: {e}")