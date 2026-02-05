from pydantic import BaseModel
from typing import List, Optional, Any


# --- Brands ---
class BrandItem(BaseModel):
    number: str
    brand: str
    des_text: str


class BrandsResponse(BaseModel):
    result: str = "ok"
    data: List[BrandItem]


# --- Offers ---
class OfferItem(BaseModel):
    oem: str
    make_name: str
    detail_name: str
    cost: float
    qnt: int
    min_delivery_day: int
    max_delivery_day: int
    min_qnt: int
    sup_logo: str
    stat_group: int
    system_hash: str
    weight: float
    volume: float
    sys_info: dict


class OffersResponse(BaseModel):
    result: str = "ok"
    data: List[OfferItem]

