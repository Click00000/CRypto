from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import Exchange, FlowMetric, User
from decimal import Decimal

router = APIRouter()


@router.get("/exchanges")
async def list_exchanges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all exchanges"""
    exchanges = db.query(Exchange).all()
    return [
        {
            "id": str(ex.id),
            "name": ex.name,
            "slug": ex.slug,
            "created_at": ex.created_at.isoformat()
        }
        for ex in exchanges
    ]


@router.get("/exchanges/{exchange_id}/flows")
async def get_exchange_flows(
    exchange_id: str,
    asset: Optional[str] = Query(None),
    window: str = Query("1h"),
    from_time: Optional[str] = Query(None, alias="from"),
    to_time: Optional[str] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flow metrics for an exchange"""
    # Validate exchange
    exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not exchange:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Build query
    query = db.query(FlowMetric).filter(FlowMetric.exchange_id == exchange_id)
    
    if asset:
        query = query.filter(FlowMetric.asset_symbol == asset.upper())
    
    if window:
        query = query.filter(FlowMetric.window == window)
    
    if from_time:
        try:
            from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
            query = query.filter(FlowMetric.time_bucket >= from_dt)
        except ValueError:
            pass
    
    if to_time:
        try:
            to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
            query = query.filter(FlowMetric.time_bucket <= to_dt)
        except ValueError:
            pass
    
    metrics = query.order_by(FlowMetric.time_bucket.desc()).limit(1000).all()
    
    return [
        {
            "time_bucket": m.time_bucket.isoformat(),
            "window": m.window,
            "asset_symbol": m.asset_symbol,
            "inflow": str(m.inflow),
            "outflow": str(m.outflow),
            "netflow": str(m.netflow)
        }
        for m in metrics
    ]


@router.get("/assets/{symbol}/flows")
async def get_asset_flows(
    symbol: str,
    window: str = Query("1h"),
    from_time: Optional[str] = Query(None, alias="from"),
    to_time: Optional[str] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flow metrics for an asset across all exchanges"""
    query = db.query(FlowMetric).filter(FlowMetric.asset_symbol == symbol.upper())
    
    if window:
        query = query.filter(FlowMetric.window == window)
    
    if from_time:
        try:
            from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
            query = query.filter(FlowMetric.time_bucket >= from_dt)
        except ValueError:
            pass
    
    if to_time:
        try:
            to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
            query = query.filter(FlowMetric.time_bucket <= to_dt)
        except ValueError:
            pass
    
    metrics = query.order_by(FlowMetric.time_bucket.desc()).limit(1000).all()
    
    return [
        {
            "time_bucket": m.time_bucket.isoformat(),
            "window": m.window,
            "exchange_id": str(m.exchange_id) if m.exchange_id else None,
            "inflow": str(m.inflow),
            "outflow": str(m.outflow),
            "netflow": str(m.netflow)
        }
        for m in metrics
    ]
