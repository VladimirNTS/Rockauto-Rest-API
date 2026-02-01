from fastapi import FastAPI, Request, HTTPException, Depends

from app.api.search import router as search_router


app = FastAPI(title="RockAuto supplier (api_key only)")

app.include_router(search_router)



