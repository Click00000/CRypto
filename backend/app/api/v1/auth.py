from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.services.auth import AuthService
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.db.models import User
from datetime import timedelta
from app.core.config import settings

router = APIRouter()


class MagicLinkRequest(BaseModel):
    email: EmailStr
    marketing_opt_in: bool = False


class MagicLinkConsume(BaseModel):
    token: str


@router.post("/request-link")
async def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """Request magic link - no auth required"""
    auth_service = AuthService(db)
    result = auth_service.request_magic_link(
        request.email,
        request.marketing_opt_in
    )
    return result


@router.post("/consume-link")
async def consume_magic_link(
    request: MagicLinkConsume,
    response: Response,
    db: Session = Depends(get_db)
):
    """Consume magic link token and set JWT cookie - no auth required"""
    auth_service = AuthService(db)
    user = auth_service.consume_magic_link(request.token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Set HttpOnly cookie
    # Determine if we're in production (HTTPS)
    is_production = settings.APP_BASE_URL.startswith("https://")
    
    response.set_cookie(
        key="efi_session",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=is_production,  # True in production with HTTPS
        max_age=settings.JWT_EXPIRATION_HOURS * 3600
    )
    
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "plan": user.plan.value
        }
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout - clear cookie"""
    response.delete_cookie(key="efi_session")
    return {"message": "Logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
        "plan": current_user.plan.value,
        "email_verified_at": current_user.email_verified_at.isoformat() if current_user.email_verified_at else None
    }
