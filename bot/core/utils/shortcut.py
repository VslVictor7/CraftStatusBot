import requests

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