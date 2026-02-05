from typing import List, Dict, Any, Optional
import logging
import asyncio

from app.utils.exchanger import usd_to_gel
from rockauto_api import RockAutoClient


async def find_parts_by_oem(oem):
    async with RockAutoClient() as client:
        # Find a specific vehicle
        vehicle = await client.search_parts_by_number(part_number=oem)
        data = []
        for i in vehicle.parts:
            data.append({
                'oem': i.part_number,
                'brand': i.brand,
                'des_text': i.name
            })

        return data


async def find_parts_by_oem_and_make_name(
    oem: str,
    make_name: str = '',
    text: str = ''
):
    async with RockAutoClient() as client:
        # Find a specific vehicle
        vehicle = await client.search_parts_by_number(
            part_number=text + oem,
            manufacturer=make_name,
        )
        data = []
        for i in vehicle.parts:
            data.append({
                'oem': i.part_number,
                'make_name': i.brand,
                'detail_name': i.name,
                'cost': await usd_to_gel(i.price),
                'qnt': 25,
                'min_delivery_day': 0,
                'max_delivery_day': 0,
                'min_qnt': 2,
                'sup_logo': "ROCKAUTO",
                'stat_group': 0,
                'system_hash': "",
                'weight': 0.0,
                'volume': 0.0,
                'sys_info': {}
            })

        return data


async def find_list_of_parts_by_oem_and_make_name(
    articles: List[dict],
):
    async with RockAutoClient() as client:
        data = []

        for article in articles:
            vehicle = await client.search_parts_by_number(
                part_number=article['oem'],
                manufacturer=article['make_name'],
            )
            for i in vehicle.parts:
                data.append({
                    'oem': i.part_number,
                    'number': article['oem'],
                    'make_name': i.brand,
                    'detail_name': i.name,
                    'cost': await usd_to_gel(i.price),
                    'qnt': 25,
                    'min_qnt': 2,
                    'min_delivery_day': 0,
                    'max_delivery_day': 0,
                    'sup_logo': "BERG",
                    'stat_group': 0,
                    'system_hash': ""
                })

        return data



       

