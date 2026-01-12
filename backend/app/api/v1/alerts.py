from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import Alert, User

router = APIRouter()


@router.get("/alerts/live")
async def get_live_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent alerts (last 24 hours)"""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    alerts = db.query(Alert).filter(
        Alert.created_at >= cutoff
    ).order_by(Alert.created_at.desc()).limit(100).all()
    
    return [
        {
            "id": str(a.id),
            "exchange_id": str(a.exchange_id) if a.exchange_id else None,
            "asset_symbol": a.asset_symbol,
            "window": a.window,
            "z_score": str(a.z_score),
            "netflow": str(a.netflow),
            "baseline_mean": str(a.baseline_mean),
            "baseline_std": str(a.baseline_std),
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]
