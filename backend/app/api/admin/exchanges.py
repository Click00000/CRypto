from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.db.models import Exchange, User
import re

router = APIRouter()


class ExchangeCreate(BaseModel):
    name: str
    slug: str


class ExchangeUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


@router.post("/exchanges")
async def create_exchange(
    exchange: ExchangeCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new exchange"""
    # Validate slug format
    if not re.match(r"^[a-z0-9-]+$", exchange.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug must contain only lowercase letters, numbers, and hyphens"
        )
    
    # Check if slug exists
    existing = db.query(Exchange).filter(Exchange.slug == exchange.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exchange with this slug already exists"
        )
    
    new_exchange = Exchange(name=exchange.name, slug=exchange.slug)
    db.add(new_exchange)
    db.commit()
    db.refresh(new_exchange)
    
    return {
        "id": str(new_exchange.id),
        "name": new_exchange.name,
        "slug": new_exchange.slug,
        "created_at": new_exchange.created_at.isoformat()
    }


@router.patch("/exchanges/{exchange_id}")
async def update_exchange(
    exchange_id: str,
    exchange: ExchangeUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update an exchange"""
    db_exchange = db.query(Exchange).filter(Exchange.id == exchange_id).first()
    if not db_exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    if exchange.name is not None:
        db_exchange.name = exchange.name
    
    if exchange.slug is not None:
        if not re.match(r"^[a-z0-9-]+$", exchange.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug must contain only lowercase letters, numbers, and hyphens"
            )
        # Check if slug exists (excluding current)
        existing = db.query(Exchange).filter(
            Exchange.slug == exchange.slug,
            Exchange.id != exchange_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exchange with this slug already exists"
            )
        db_exchange.slug = exchange.slug
    
    db.commit()
    db.refresh(db_exchange)
    
    return {
        "id": str(db_exchange.id),
        "name": db_exchange.name,
        "slug": db_exchange.slug,
        "created_at": db_exchange.created_at.isoformat()
    }


@router.get("/exchanges")
async def list_exchanges_admin(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all exchanges (admin)"""
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
