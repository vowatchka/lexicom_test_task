from fastapi import APIRouter

from .addresses import addresses_router

__all__ = ["api_router"]

api_router = APIRouter(prefix="/api")
api_router.include_router(addresses_router)
