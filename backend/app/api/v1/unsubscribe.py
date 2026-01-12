from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import AuthService

router = APIRouter()


@router.get("/unsubscribe")
async def unsubscribe(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Unsubscribe from marketing emails - no auth required"""
    auth_service = AuthService(db)
    success = auth_service.unsubscribe(token)
    
    if not success:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid unsubscribe token"
        )
    
    return {"message": "Successfully unsubscribed"}
