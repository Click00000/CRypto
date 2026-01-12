from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.db.models import SyncState, User, Chain

router = APIRouter()


class SyncStateReset(BaseModel):
    chain: str
    last_processed_block: Optional[int] = None
    last_processed_height: Optional[int] = None


@router.get("/sync-state")
async def get_sync_state(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get sync state for all chains"""
    states = db.query(SyncState).all()
    return [
        {
            "chain": state.chain.value,
            "last_processed_block": state.last_processed_block,
            "last_processed_height": state.last_processed_height,
            "updated_at": state.updated_at.isoformat()
        }
        for state in states
    ]


@router.post("/sync/reset")
async def reset_sync_state(
    reset: SyncStateReset,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reset sync state (optional: set last processed values)"""
    try:
        chain_enum = Chain(reset.chain.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chain must be EVM or BTC"
        )
    
    state = db.query(SyncState).filter(SyncState.chain == chain_enum).first()
    if not state:
        state = SyncState(chain=chain_enum)
        db.add(state)
    
    if reset.last_processed_block is not None:
        state.last_processed_block = reset.last_processed_block
    
    if reset.last_processed_height is not None:
        state.last_processed_height = reset.last_processed_height
    
    db.commit()
    db.refresh(state)
    
    return {
        "chain": state.chain.value,
        "last_processed_block": state.last_processed_block,
        "last_processed_height": state.last_processed_height,
        "updated_at": state.updated_at.isoformat()
    }


@router.post("/jobs/resync")
async def trigger_resync(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Trigger a resync job (enqueue ingestion tasks)"""
    try:
        import redis
        from app.core.config import settings
        
        # Connect to Redis and enqueue tasks
        r = redis.from_url(settings.REDIS_URL)
        r.lpush("celery", '{"id": "evm-resync", "task": "evm_sync_task", "args": [], "kwargs": {}}')
        r.lpush("celery", '{"id": "btc-resync", "task": "btc_sync_task", "args": [], "kwargs": {}}')
        
        return {"message": "Resync jobs enqueued"}
    except Exception as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue jobs: {str(e)}"
        )
