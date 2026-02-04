from fastapi import APIRouter, Query, Body, Security
from typing import List, Optional
from app.auth import check_api_key, get_api_key
from app.api.schemas import (
    BrandsResponse, BrandItem,
    OffersResponse, OfferItem,
    BatchRequest
)
from app.utils.rockauto import find_parts_by_oem, find_parts_by_oem_and_make_name

router = APIRouter(prefix="", tags=["search"])


@router.get("/backend/price_items/api/v1/search/get_brands_by_oem", response_model=BrandsResponse)
@router.get("/api/v1/search/get_brands_by_oem", response_model=BrandsResponse)
async def get_brands_by_oem(
    oem: str = Query(..., description="OEM number"),
    api_key: str = Query(...)
):
    check_api_key(api_key)

    data = await find_parts_by_oem(oem)

    return BrandsResponse(result="ok", data=data)


@router.get("/api/v1/search/get_offers_by_oem_and_make_name", response_model=OffersResponse)
@router.get("/backend/price_items/api/v1/search/get_offers_by_oem_and_make_name", response_model=OffersResponse)
async def get_offers_by_oem_and_make_name(
    oem: str = Query(...),
    make_name: Optional[str] = Query(None),
    without_cross: Optional[bool] = Query(None),
    text: Optional[str] = Query(None),
    api_key: str = Query(...)
):
    """
    GET /get_offers_by_oem_and_make_name?oem=...&make_name=...
    """
    check_api_key(api_key)
    
    data = await find_parts_by_oem_and_make_name(oem)

    return OffersResponse(result="ok", data=data)


@router.post("/backend/price_items/api/v1/search/get_offers_by_oem_and_make_name", response_model=OffersResponse)
@router.post("/api/v1/search/get_offers_by_oem_and_make_name", response_model=OffersResponse)
async def get_offers_batch(
    payload: BatchRequest = Body(...),
    api_key: str = Query(...)
):
    """
    POST /get_offers_by_oem_and_make_name
    Body: { "oem_list": [...], "articles": [{ "oem":"...", "brand":"..." }, ...] }
    """
    check_api_key(api_key)
    return OffersResponse(result="ok", data=[])

