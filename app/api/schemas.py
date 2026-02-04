from pydantic import BaseModel
from typing import List, Optional, Any


# --- Brands ---
class BrandItem(BaseModel):
    oem: str 
    brand: str
    des_text: Optional[str] = None


class BrandsResponse(BaseModel):
    result: str = "ok"
    data: List[BrandItem] = []


# --- Offers ---
class OfferItem(BaseModel):
    oem: str
    make_name: Optional[str] = None
    detail_name: Optional[str] = None
    cost: Optional[float] = None
    qnt: Optional[int] = None
    min_delivery_day: Optional[int] = None
    max_delivery_day: Optional[int] = None
    goods_img_url: Optional[list[str]] = []
    supplier_code: Optional[str] = None
    system_hash: Optional[str] = None
    extra: Optional[Any] = None


class OffersResponse(BaseModel):
    result: str = "ok"
    data: List[OfferItem] = []


# --- Batch request ---
class BatchArticle(BaseModel):
    oem: str
    brand: Optional[str] = None


class BatchRequest(BaseModel):
    articles: Optional[List[BatchArticle]] = None
    category_id: Optional[int] = None

