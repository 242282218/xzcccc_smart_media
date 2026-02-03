from fastapi import APIRouter
from app.api.v1.endpoints import scrape, rename

api_router = APIRouter()

api_router.include_router(scrape.router, prefix="/scrape", tags=["Scrape V1"])
api_router.include_router(rename.router, prefix="/rename", tags=["Rename V1"])
