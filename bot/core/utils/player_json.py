import json
import os
import discord
import requests

def player_stats(path, username):

    if not os.path.exists(path):
        print(f"Erro: O arquivo de estatísticas para {username} não foi encontrado.")
        return None
    else:
        with open(path, "r", encoding="utf-8") as file:
            stats = json.load(file)

        custom_stats = stats.get("stats", {}).get("minecraft:custom", {})
        mined_stats = stats.get("stats", {}).get("minecraft:mined", {})
        item_broken_stats = stats.get("stats", {}).get("minecraft:broken", {})
        item_crafted_stats = stats.get("stats", {}).get("minecraft:crafted", {})
        item_used_stats = stats.get("stats", {}).get("minecraft:used", {})
        item_picked_up = stats.get("stats", {}).get("minecraft:picked_up", {})
        item_dropped = stats.get("stats", {}).get("minecraft:dropped", {})
        mobs_killed = stats.get("stats", {}).get("minecraft:killed", {})
        mobs_killed_player = stats.get("stats", {}).get("minecraft:killed_by", {})

        play_time = custom_stats.get("minecraft:play_time", 0) // 20
        jumps = custom_stats.get("minecraft:jump", 0)
        walked_cm = custom_stats.get("minecraft:walk_one_cm", 0)
        deaths = custom_stats.get("minecraft:deaths", 0)
        time_since_death = custom_stats.get("minecraft:time_since_death", 0) // 20

        total_mined = sum(mined_stats.values())
        item_broken = sum(item_broken_stats.values())
        item_crafted = sum(item_crafted_stats.values())
        item_used = sum(item_used_stats.values())
        item_picked_up = sum(item_picked_up.values())
        item_dropped = sum(item_dropped.values())
        mobs_killed = sum(mobs_killed.values())
        mobs_killed_player = sum(mobs_killed_player.values())

        embed = discord.Embed(title=f"Estatísticas de {username}", color=0x7289DA)

        embed.add_field(
            name="Informações do Jogador",
            value=(
                f"⏳ **Tempo jogado**: {play_time // 3600}h {play_time % 3600 // 60}m {play_time % 60}s\n"
                f"🏃‍♂️ **Distância percorrida**: {walked_cm // 100000} km e {(walked_cm % 100000) // 100} metros\n"
                f"⬆️ **Saltos**: {jumps}\n"
                f"💀 **Mortes**: {deaths}\n"
                f"⏱️ **Tempo desde a última morte**: {time_since_death // 3600}h {time_since_death % 3600 // 60}m {time_since_death % 60}s"
            ),
            inline=False
        )

        embed.add_field(
            name="Itens",
            value=(
                f"⛏️ **Blocos minerados**: {total_mined}\n"
                f"🔨 **Itens quebrados**: {item_broken}\n"
                f"🛠️ **Itens craftados**: {item_crafted}\n"
                f"🔧 **Itens usados**: {item_used}\n"
                f"📦 **Itens coletados**: {item_picked_up}\n"
                f"📤 **Itens descartados**: {item_dropped}"
            ),
            inline=False
        )

        embed.add_field(
            name="Mobs",
            value=(
                f"⚔️ **Mobs mortos**: {mobs_killed}\n"
                f"💀 **Morte contra Mobs**: {mobs_killed_player}"
            ),
            inline=False
        )

        return embed

def get_uuid_from_username(username):
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        response.raise_for_status()

        data = response.json()
        if not data or 'id' not in data:
            raise ValueError(f"O nome de usuário '{username}' não foi encontrado na API Mojang.")
        uuid_clean = data['id']

        uuid_with_hyphen = f"{uuid_clean[:8]}-{uuid_clean[8:12]}-{uuid_clean[12:16]}-{uuid_clean[16:20]}-{uuid_clean[20:]}"

        return uuid_with_hyphen

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro ao acessar a API Mojang: {e}")