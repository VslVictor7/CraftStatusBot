import discord
import os
import json
import pytz
from dotenv import load_dotenv
from datetime import datetime
from musica import lyrics_finder
from minecraft.utils import shortcut, player_json

load_dotenv()

JSON_PATH = os.getenv('JSON_PATH')

def create_embed(title, description, color):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.timestamp = datetime.now(pytz.timezone("America/Sao_Paulo"))
    return embed

async def setup_commands(bot):

    @bot.tree.command(name="uptime", description="Mostra o tempo que o servidor está online.")
    async def uptime(interaction: discord.Interaction):
        if bot.uptime_start:
            current_time = datetime.now(pytz.timezone('America/Sao_Paulo'))
            uptime_duration = current_time - bot.uptime_start
            hours, remainder = divmod(uptime_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            uptime_message = f"O servidor está online há {hours} horas, {minutes} minutos e {seconds} segundos."
            embed = create_embed("Uptime do Servidor", uptime_message, 0x7289DA)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("O servidor está offline no momento.", ephemeral=True)

    @bot.tree.command(name="ping", description="Verifica o ping do servidor Minecraft")
    async def ping(interaction: discord.Interaction):
        try:
            latency = bot.server.ping()
            latency = round(latency, 2)
            latency_text = f"{latency} ms"
            embed = create_embed("Latência do Servidor", latency_text, 0x7289DA)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            latency_text = f"Erro ao obter latência: {e}"
            embed = create_embed("Latência do Servidor", latency_text, 0x7289DA)
            await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="letra", description="Busca a letra de uma música no Genius")
    async def fetch_lyrics(interaction: discord.Interaction, song_title: str):
        await interaction.response.defer()
        final_title, lyrics = lyrics_finder.get_song_lyrics(song_title)

        if final_title == "Nenhuma música encontrada.":
            await interaction.followup.send(final_title)
            return

        partes_lyricas = lyrics_finder.split_lyrics(lyrics)
        for parte in partes_lyricas:
            embed = create_embed(f"Letra de {final_title}", parte, 0x7289DA)
            await interaction.followup.send(embed=embed)

    @bot.tree.command(name="stats", description="Mostra estatísticas do jogador Minecraft.")
    async def player_information(interaction: discord.Interaction, username: str):

        stats_path = f"{JSON_PATH}{username}.lnk"

        try:

            path = shortcut.resolve_shortcut(stats_path)

            stats_message = player_json.player_stats(path, username)

            await interaction.response.send_message(embed=stats_message)

        except FileNotFoundError:
            await interaction.response.send_message(
                f"Arquivo de estatísticas para {username} não encontrado. Certifique de escrever corretamente o nome de usuário!", ephemeral=True
            )
        except json.JSONDecodeError:
            await interaction.response.send_message(
                f"O arquivo de estatísticas de {username} está corrompido ou não é válido.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Ocorreu um erro ao buscar as estatísticas: {e}", ephemeral=True
            )

    @bot.tree.command(name="help", description="Exibe a lista de comandos disponíveis.")
    async def help_command(interaction: discord.Interaction):
        embed = create_embed(
            title="Lista de Comandos",
            description="Aqui estão os comandos disponíveis no bot:",
            color=0x7289DA
        )
        embed.add_field(
            name="/uptime",
            value="Mostra o tempo que o servidor está online.",
            inline=False
        )
        embed.add_field(
            name="/ping",
            value="Verifica o ping do servidor Minecraft.",
            inline=False
        )
        embed.add_field(
            name="/letra <título da música>",
            value="Busca a letra de uma música no Genius.",
            inline=False
        )
        embed.add_field(
            name="/stats <username>",
            value="Mostra estatísticas do jogador Minecraft com base no nome de usuário.",
            inline=False
        )
        embed.add_field(
            name="/help",
            value="Exibe esta lista de comandos.",
            inline=False
        )
        embed.set_footer(text="Utilize os comandos para explorar as funcionalidades do bot.")

        await interaction.response.send_message(embed=embed)