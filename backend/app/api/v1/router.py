from fastapi import APIRouter
from app.api.v1 import auth, exchanges, alerts, unsubscribe, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(exchanges.router, tags=["exchanges"])
api_router.include_router(alerts.router, tags=["alerts"])
api_router.include_router(unsubscribe.router, tags=["unsubscribe"])
api_router.include_router(health.router, tags=["health"])
