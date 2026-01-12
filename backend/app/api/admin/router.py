from fastapi import APIRouter
from app.api.admin import exchanges, addresses, sync

admin_router = APIRouter(prefix="/admin", tags=["admin"])

admin_router.include_router(exchanges.router)
admin_router.include_router(addresses.router)
admin_router.include_router(sync.router)
