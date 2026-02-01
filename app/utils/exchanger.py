import asyncio
from datetime import datetime
from httpx import AsyncClient


async def usd_to_gel(amount):

    params = {
        'from': 'USD',
        'to': 'GEL',
        'date': datetime.today().strftime('%Y-%m-%d'),
        'amount': str(amount),
        'format': 'json',
    }
    
    async with AsyncClient() as client:
        response = await client.get('https://api.fxratesapi.com/convert', params=params)
        
        print(response.json()['result'])
        return response.json()['result']


if __name__ == "__main__":
    asyncio.run(usd_to_gel(1))

