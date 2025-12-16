import json
import os
import discord
import requests
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')

async def player_stats(path, username):
    embed = await player_stats_formation(path, username)
    return embed

async def player_stats_formation(path, username):

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
        deaths = custom_stats.get("minecraft:deaths", 0)
        time_since_death = custom_stats.get("minecraft:time_since_death", 0) // 20
        damage_dealt = custom_stats.get("minecraft:damage_dealt", 0)
        damage_taken = custom_stats.get("minecraft:damage_taken", 0)
        fish_caught = custom_stats.get("minecraft:fish_caught", 0)

        walked_cm = custom_stats.get("minecraft:walk_one_cm", 0)
        sprinted_cm = custom_stats.get("minecraft:sprint_one_cm", 0)
        boat_cm = custom_stats.get("minecraft:boat_one_cm", 0)
        elytra_cm = custom_stats.get("minecraft:aviate_one_cm", 0)
        horse_cm = custom_stats.get("minecraft:horse_one_cm", 0)
        minecart_cm = custom_stats.get("minecraft:minecart_one_cm", 0)
        

        most_killed_mob = max(mobs_killed, key=mobs_killed.get)
        most_killed_count = mobs_killed[most_killed_mob]
        translation_mob = await api_fetch(most_killed_mob)


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
                f"🚶‍♂️ **Distância andando**: {walked_cm // 100000} km e {(walked_cm % 100000) // 100} metros\n"
                f"🏃‍♂️ **Distância correndo**: {sprinted_cm // 100000} km e {(sprinted_cm % 100000) // 100} metros\n"
                f"⬆️ **Saltos**: {jumps}\n"
                f"💀 **Mortes**: {deaths} vezes\n"
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
                f"📤 **Itens dropados**: {item_dropped}\n"
            ),
            inline=False
        )

        embed.add_field(
            name="Ações",
            value=(
                f"🗡️ **Mob mais morto:**: {translation_mob}: {most_killed_count} vezes\n"
                f"⚔️ **Mobs mortos**: {mobs_killed}\n"
                f"💀 **Morreu contra Mobs**: {mobs_killed_player} vezes\n"
                f"💥 **Dano causado**: {damage_dealt}\n"
                f"💔 **Dano sofrido**: {damage_taken}\n"
                f"🐟 **Peixes pescados**: {fish_caught}"
            ),
            inline=False
        )

        embed.add_field(
            name="Transportes",
            value=(
                f"🚤 **Distância de barco**: {boat_cm // 100000} km e {(boat_cm % 100000) // 100} metros\n"
                f"🐎 **Distância de cavalo**: {horse_cm // 100000} km e {(horse_cm % 100000) // 100} metros\n"
                f"🕊️ **Distância de elytra**: {elytra_cm // 100000} km e {(elytra_cm % 100000) // 100} metros\n"
                f"🚆 **Distância de minecart**: {minecart_cm // 100000} km e {(minecart_cm % 100000) // 100} metros\n"
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
    
async def api_fetch(most_killed_mob):

    mob_name = most_killed_mob.split(":")[1].replace("_", " ")
    mob_data = await fetch_data_from_api(f"{API_URL}/images/{mob_name}")
    mobs = await fetch_data_from_api(f"{API_URL}/mobs")

    entity_name = mob_data.get('name')
    full_name = entity_name.replace("_", " ")

    entity = mobs.get(full_name.strip(), full_name)
    return entity

async def fetch_data_from_api(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"[BOT ERROR] Erro ao buscar dados da API: {response.status}")
                    return {}
    except Exception as e:
        print(f"[BOT ERROR] Erro ao buscar dados da API: {e}")
        return {}