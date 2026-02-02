import asyncio
from datetime import datetime
from httpx import AsyncClient


async def usd_to_gel(amount):

    params = {
        'from': 'EUR',
        'to': 'GEL',
        'date': datetime.today().strftime('%Y-%m-%d'),
        'amount': str(amount),
        'format': 'json',
    }
    
    if '€' in amount:
        amount = amount.replace('€', '').strip()
        async with AsyncClient() as client:
            response = await client.get('https://api.fxratesapi.com/convert', params=params)
            
            return response.json()['result']

    elif '$' in amount:
        params['from'] = 'USD'
        amount = amount.replace('$', '').strip()
        async with AsyncClient() as client:
            response = await client.get('https://api.fxratesapi.com/convert', params=params)
            
            return response.json()['result']


if __name__ == "__main__":
    asyncio.run(usd_to_gel(1))

