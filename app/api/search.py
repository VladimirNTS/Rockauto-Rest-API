from fastapi import APIRouter, Query, Body, Security
from typing import List, Optional
from app.auth import get_api_key
from app.api.schemas import (
    BrandsResponse, BrandItem,
    OffersResponse, OfferItem,
    BatchRequest
)
from app.utils.rockauto import find_parts_by_oem, find_parts_by_oem_and_make_name

router = APIRouter(prefix="/backend/price_items/api/v1/search", tags=["search"])


@router.get("/get_brands_by_oem", response_model=BrandsResponse)
async def get_brands_by_oem(
    oem: str = Query(..., description="OEM number"),
    auth: dict = Security(get_api_key)
):
    data = await find_parts_by_oem(oem)

    return BrandsResponse(result="ok", data=data)


@router.get("/get_offers_by_oem_and_make_name", response_model=OffersResponse)
async def get_offers_by_oem_and_make_name(
    oem: Optional[str] = Query(None),
    make_name: Optional[str] = Query(None),
    without_cross: Optional[bool] = Query(None),
    text: Optional[str] = Query(None),
    auth: dict = Security(get_api_key)
):
    """
    GET /get_offers_by_oem_and_make_name?oem=...&make_name=...
    """
    
    data = await find_parts_by_oem_and_make_name(oem)

    return OffersResponse(result="ok", data=data)


@router.post("/get_offers_by_oem_and_make_name", response_model=OffersResponse)
async def get_offers_batch(
    payload: BatchRequest = Body(...),
    auth: dict = Security(get_api_key)
):
    """
    POST /get_offers_by_oem_and_make_name
    Body: { "oem_list": [...], "articles": [{ "oem":"...", "brand":"..." }, ...] }
    """
    return OffersResponse(result="ok", data=[])

