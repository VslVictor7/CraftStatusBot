import requests

def get_uuid_from_username(username):
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        response.raise_for_status()
        data = response.json()
        uuid_clean = data['id']

        uuid_with_hyphen = f"{uuid_clean[:8]}-{uuid_clean[8:12]}-{uuid_clean[12:16]}-{uuid_clean[16:20]}-{uuid_clean[20:]}"

        return uuid_with_hyphen

    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter UUID: {e}")
        return None