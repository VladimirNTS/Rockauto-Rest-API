from httpx import AsyncClient


async def get_proxy():
    headers = {
        'accept': 'application/json',
        'X-Api-Key': 'v24PTSA8.yvHuGz2KbKvflBMnVLIsE5UjCyzq6ZTK',
    }

    async with AsyncClient() as client:
        response = client.get('https://app.cyberyozh.com/api/v1/proxies/history/', headers=headers)
    
