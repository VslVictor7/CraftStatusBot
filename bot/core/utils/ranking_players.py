import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

JSON_PATH = os.getenv('JSON_PATH')

# Cache simples para armazenar os nomes dos jogadores
uuid_cache = {}

def get_all_play_times(directory):
    if not os.path.exists(directory):
        print("Erro: O diretório especificado não foi encontrado.")
        return []

    player_times = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):  # Considera apenas arquivos JSON
            file_path = os.path.join(directory, file_name)

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    stats = json.load(file)

                # Extrai tempo de jogo do JSON
                custom_stats = stats.get("stats", {}).get("minecraft:custom", {})
                play_time = custom_stats.get("minecraft:play_time", 0) // 20  # Tempo em segundos

                # Adiciona o UUID (presumindo que o nome do arquivo é o UUID do jogador)
                uuid = os.path.splitext(file_name)[0]
                player_times.append((uuid, play_time))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Erro ao processar o arquivo {file_name}: {e}")

    return player_times


def display_top_players(player_times, top_n=5):
    sorted_players = sorted(player_times, key=lambda x: x[1], reverse=True)
    return sorted_players[:top_n]


async def get_username_from_uuid(uuid):

    if uuid in uuid_cache:
        return uuid_cache[uuid]

    try:
        response = requests.get(f"https://api.minetools.eu/uuid/{uuid}")
        response.raise_for_status()

        data = response.json()
        if not data or "name" not in data:
            raise ValueError(f"O UUID '{uuid}' não foi encontrado na API Mojang.")

        username = data["name"]
        uuid_cache[uuid] = username
        return username

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API Mojang para o UUID '{uuid}': {e}")
        return "Nome não encontrado"
    except ValueError as e:
        print(e)
        return "Nome não encontrado"
