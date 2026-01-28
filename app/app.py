from fastapi import FastAPI, Request, HTTPException, Depends
import os
import secrets


app = FastAPI(title="RockAuto supplier (api_key only)")


API_KEYS = {
    # ключ : meta
    os.getenv("PARTS_SOFT_API_KEY", "test_static_key_very_long_random"): {
        "customer_id": 5124,
    }
}

async def require_api_key(request: Request):
    q = dict(request.query_params)
    api_key = q.get("api_key") or request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="api_key required")

    # безопасное сравнение
    for valid_key, meta in API_KEYS.items():
        if secrets.compare_digest(api_key, valid_key):
            return {"api_key": valid_key, **meta}

    raise HTTPException(status_code=403, detail="invalid api_key")


@app.get("/backend/price_items/api/v1/search/get_brands_by_oem")
async def get_brands_by_oem(oem: str, auth=Depends(require_api_key)):
    return {
        "result": "ok",
        "data": [
            {"number": oem, "brand": "DOLZ", "des_text": "Водяной насос"}
        ]
    }

@app.get("/backend/price_items/api/v1/search/get_offers_by_oem_and_make_name")
async def get_offers(oem: str | None = None, text: str | None = None, make_name: str | None = None, auth=Depends(require_api_key)):
    return {"result": "ok", "items": []}








