import asyncio
from datetime import datetime
from httpx import AsyncClient


async def usd_to_gel(amount):

    params = {
        'from': 'EUR',
        'to': 'GEL',
        'date': datetime.today().strftime('%Y-%m-%d'),
        'amount': 0,
        'format': 'json',
    }
    
    if '€' in amount:
        amount = float(amount.replace('€', '').strip())
        params['amount'] = amount
        async with AsyncClient() as client:
            response = await client.get('https://api.fxratesapi.com/convert', params=params)
            
            return response.json()['result']

    elif '$' in amount:
        params['from'] = 'USD'
        amount = float(amount.replace('$', '').strip())
        params['amount'] = amount
        async with AsyncClient() as client:
            response = await client.get('https://api.fxratesapi.com/convert', params=params)
            
            return response.json()['result']


if __name__ == "__main__":
    asyncio.run(usd_to_gel(1))

