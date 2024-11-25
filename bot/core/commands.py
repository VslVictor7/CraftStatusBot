import discord
import os
import json
import pytz
from dotenv import load_dotenv
from datetime import datetime
from mcstatus import JavaServer
from utils import player_json
from musica import lyrics_finder
from utils import shortcut

load_dotenv()

JSON_PATH = os.getenv('JSON_PATH')
IP_ADRESS = os.getenv('MINECRAFT_SERVER')

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

    @bot.tree.command(name="limpar_dms", description="Apaga mensagens do bot na DM atual.")
    async def limpar_dms(interaction: discord.Interaction):
        # Verifica se está em um canal de mensagem direta (DM)
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.defer(ephemeral=True)  # Defere a resposta (indica que vai demorar um pouco)

            count = 0
            async for message in interaction.channel.history(limit=100):
                if message.author == bot.user:
                    await message.delete()
                    count += 1

            # Envia a resposta final
            await interaction.followup.send(f"{count} mensagens apagadas.")
        else:
            # Resposta caso o comando não esteja em uma DM
            await interaction.response.send_message(
                "Este comando só funciona em mensagens diretas (DMs).",
                ephemeral=True,
            )

    @bot.tree.command(name="limpar", description="Apaga mensagens do canal atual no servidor.")
    async def limpar(interaction: discord.Interaction, quantidade: int):
        if isinstance(interaction.channel, discord.TextChannel):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message(
                    "Você não tem permissão para usar este comando.",
                    ephemeral=True
                )
                return

            if quantidade < 1:
                await interaction.response.send_message(
                    "Por favor, insira um número válido de mensagens para apagar (no mínimo 1).",
                    ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)  # Indica que a resposta pode levar algum tempo

            try:
                deleted_messages = await interaction.channel.purge(limit=quantidade)
                await interaction.followup.send(
                    f"{len(deleted_messages)} mensagens apagadas com sucesso!",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "O bot não tem permissão para apagar mensagens neste canal.",
                    ephemeral=True
                )
            except discord.HTTPException as e:
                await interaction.followup.send(
                    f"Ocorreu um erro ao tentar apagar as mensagens: {e}",
                    ephemeral=True
                )
            else:
                # Caso o comando seja usado em uma DM
                await interaction.response.send_message(
                    "Este comando só pode ser usado em canais de texto do servidor.",
                    ephemeral=True
                )


    @bot.tree.command(name="ping", description="Verifica o ping do servidor Minecraft")
    async def ping(interaction: discord.Interaction):
        try:
            server = JavaServer.lookup(f"{IP_ADRESS}:{JavaServer.DEFAULT_PORT}")
            latency = server.ping()
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

        try:

            uuid = shortcut.get_uuid_from_username(username)

            stats_path = f"{JSON_PATH}{uuid}.json"

            stats_message = player_json.player_stats(stats_path, username)

            await interaction.response.send_message(embed=stats_message)

        except FileNotFoundError:
            await interaction.followup.send(
                f"Arquivo de estatísticas para {username} não encontrado. Certifique-se de escrever corretamente o nome de usuário!",
                ephemeral=True
            )
        except json.JSONDecodeError:
            await interaction.followup.send(
                f"O arquivo de estatísticas de {username} está corrompido ou não é válido.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"Ocorreu um erro ao buscar as estatísticas: {e}",
                ephemeral=True
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
        embed.add_field(
            name="/limpar",
            value="Limpa o chat do canal onde o comando vai ser feito.",
            inline=False
        )
        embed.add_field(
            name="/limpar_dms",
            value="Limpa a dm do bot, comando deve ser feito na dm e não chat normal.",
            inline=False
        )
        embed.set_footer(text="Utilize os comandos para explorar as funcionalidades do bot.")

        await interaction.response.send_message(embed=embed)
