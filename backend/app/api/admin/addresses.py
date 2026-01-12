from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.db.models import LabeledAddress, Exchange, Cluster, User, Chain, AddressLabel
import uuid

router = APIRouter()


class AddressCreate(BaseModel):
    exchange_id: str
    chain: str  # "EVM" or "BTC"
    address: str
    label: str  # "hot", "cold", "deposit", "reserve"
    cluster_id: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    cluster_id: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


@router.post("/addresses")
async def create_address(
    address: AddressCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new labeled address"""
    # Validate exchange
    exchange = db.query(Exchange).filter(Exchange.id == address.exchange_id).first()
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Validate chain
    try:
        chain_enum = Chain(address.chain.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chain must be EVM or BTC"
        )
    
    # Validate label
    try:
        label_enum = AddressLabel(address.label.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Label must be hot, cold, deposit, or reserve"
        )
    
    # Validate cluster if provided
    cluster_id_uuid = None
    if address.cluster_id:
        try:
            cluster_id_uuid = uuid.UUID(address.cluster_id)
            cluster = db.query(Cluster).filter(Cluster.id == cluster_id_uuid).first()
            if not cluster or cluster.exchange_id != uuid.UUID(address.exchange_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cluster not found or doesn't belong to this exchange"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cluster_id format"
            )
    
    # Normalize address (lowercase for EVM)
    normalized_address = address.address.lower() if chain_enum == Chain.EVM else address.address
    
    # Check for duplicate
    existing = db.query(LabeledAddress).filter(
        LabeledAddress.address == normalized_address,
        LabeledAddress.chain == chain_enum
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address already exists for this chain"
        )
    
    new_address = LabeledAddress(
        exchange_id=uuid.UUID(address.exchange_id),
        chain=chain_enum,
        address=normalized_address,
        label=label_enum,
        cluster_id=cluster_id_uuid,
        is_active=address.is_active,
        notes=address.notes
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    
    return {
        "id": str(new_address.id),
        "exchange_id": str(new_address.exchange_id),
        "chain": new_address.chain.value,
        "address": new_address.address,
        "label": new_address.label.value,
        "cluster_id": str(new_address.cluster_id) if new_address.cluster_id else None,
        "is_active": new_address.is_active,
        "notes": new_address.notes,
        "created_at": new_address.created_at.isoformat()
    }


@router.patch("/addresses/{address_id}")
async def update_address(
    address_id: str,
    address: AddressUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a labeled address"""
    try:
        addr_id_uuid = uuid.UUID(address_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid address_id format"
        )
    
    db_address = db.query(LabeledAddress).filter(LabeledAddress.id == addr_id_uuid).first()
    if not db_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    if address.label is not None:
        try:
            db_address.label = AddressLabel(address.label.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Label must be hot, cold, deposit, or reserve"
            )
    
    if address.cluster_id is not None:
        if address.cluster_id == "":
            db_address.cluster_id = None
        else:
            try:
                cluster_id_uuid = uuid.UUID(address.cluster_id)
                cluster = db.query(Cluster).filter(Cluster.id == cluster_id_uuid).first()
                if not cluster or cluster.exchange_id != db_address.exchange_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cluster not found or doesn't belong to this exchange"
                    )
                db_address.cluster_id = cluster_id_uuid
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid cluster_id format"
                )
    
    if address.is_active is not None:
        db_address.is_active = address.is_active
    
    if address.notes is not None:
        db_address.notes = address.notes
    
    db.commit()
    db.refresh(db_address)
    
    return {
        "id": str(db_address.id),
        "exchange_id": str(db_address.exchange_id),
        "chain": db_address.chain.value,
        "address": db_address.address,
        "label": db_address.label.value,
        "cluster_id": str(db_address.cluster_id) if db_address.cluster_id else None,
        "is_active": db_address.is_active,
        "notes": db_address.notes,
        "created_at": db_address.created_at.isoformat()
    }


@router.get("/addresses")
async def list_addresses(
    exchange_id: Optional[str] = Query(None),
    chain: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List labeled addresses with filters"""
    query = db.query(LabeledAddress)
    
    if exchange_id:
        try:
            query = query.filter(LabeledAddress.exchange_id == uuid.UUID(exchange_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid exchange_id format"
            )
    
    if chain:
        try:
            chain_enum = Chain(chain.upper())
            query = query.filter(LabeledAddress.chain == chain_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chain must be EVM or BTC"
            )
    
    if is_active is not None:
        query = query.filter(LabeledAddress.is_active == is_active)
    
    addresses = query.all()
    
    return [
        {
            "id": str(addr.id),
            "exchange_id": str(addr.exchange_id),
            "chain": addr.chain.value,
            "address": addr.address,
            "label": addr.label.value,
            "cluster_id": str(addr.cluster_id) if addr.cluster_id else None,
            "is_active": addr.is_active,
            "notes": addr.notes,
            "created_at": addr.created_at.isoformat()
        }
        for addr in addresses
    ]
