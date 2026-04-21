from httpx import AsyncClient
import asyncio
from datetime import datetime


API_URL = "https://app.cyberyozh.com/api/v1/proxies/history/"
API_KEY = "v24PTSA8.yvHuGz2KbKvflBMnVLIsE5UjCyzq6ZTK"


async def get_proxy() -> str | None:
    headers = {
        "accept": "application/json",
        "X-Api-Key": API_KEY,
    }

    async with AsyncClient() as client:
        response = await client.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

    proxies = data.get("results", [])

    # фильтр активных
    active_proxies = [
        p for p in proxies
        if not p["expired"] and p["system_status"] == "active"
    ]

    if not active_proxies:
        return None

    # самый старый
    oldest = min(
        active_proxies,
        key=lambda p: datetime.fromisoformat(
            p["access_starts_at"].replace("Z", "+00:00")
        )
    )

    # сборка строки прокси
    return(
        f"http://{oldest['connection_login']}:"
        f"{oldest['connection_password']}@"
        f"{oldest['connection_host']}:"
        f"{oldest['connection_port']}"
    )

#asyncio.run(get_proxy())

