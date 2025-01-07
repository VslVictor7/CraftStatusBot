import aiohttp

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