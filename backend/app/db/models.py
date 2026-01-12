from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Numeric, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.session import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class UserPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Chain(str, enum.Enum):
    EVM = "EVM"
    BTC = "BTC"


class AddressLabel(str, enum.Enum):
    HOT = "hot"
    COLD = "cold"
    DEPOSIT = "deposit"
    RESERVE = "reserve"


class TransferDirection(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    plan = Column(SQLEnum(UserPlan), default=UserPlan.FREE, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    marketing_opt_in = Column(Boolean, default=False, nullable=False)
    marketing_opt_in_at = Column(DateTime, nullable=True)
    unsubscribe_token = Column(String(255), unique=True, nullable=True, index=True)
    unsubscribed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MagicLinkToken(Base):
    __tablename__ = "magic_link_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", backref="magic_link_tokens")


class Exchange(Base):
    __tablename__ = "exchanges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    addresses = relationship("LabeledAddress", back_populates="exchange", cascade="all, delete-orphan")
    clusters = relationship("Cluster", back_populates="exchange", cascade="all, delete-orphan")


class Cluster(Base):
    __tablename__ = "clusters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    exchange = relationship("Exchange", back_populates="clusters")
    addresses = relationship("LabeledAddress", back_populates="cluster")


class LabeledAddress(Base):
    __tablename__ = "labeled_addresses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    chain = Column(SQLEnum(Chain), nullable=False, index=True)
    address = Column(String(255), nullable=False, index=True)
    label = Column(SQLEnum(AddressLabel), nullable=False)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    exchange = relationship("Exchange", back_populates="addresses")
    cluster = relationship("Cluster", back_populates="addresses")


class SyncState(Base):
    __tablename__ = "sync_state"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chain = Column(SQLEnum(Chain), unique=True, nullable=False, index=True)
    last_processed_block = Column(Integer, nullable=True)  # For EVM
    last_processed_height = Column(Integer, nullable=True)  # For BTC
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RawTransfer(Base):
    __tablename__ = "raw_transfers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, index=True)
    chain = Column(SQLEnum(Chain), nullable=False, index=True)
    tx_hash = Column(String(255), nullable=False, index=True)
    block_number = Column(Integer, nullable=False, index=True)
    log_index = Column(Integer, nullable=True)
    from_address = Column(String(255), nullable=False, index=True)
    to_address = Column(String(255), nullable=False, index=True)
    asset_symbol = Column(String(50), nullable=False, index=True)
    asset_address = Column(String(255), nullable=True)  # For ERC20, null for native
    amount = Column(Numeric(36, 18), nullable=False)
    direction = Column(SQLEnum(TransferDirection), nullable=False, index=True)
    exchange_from_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=True, index=True)
    exchange_to_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    exchange_from = relationship("Exchange", foreign_keys=[exchange_from_id])
    exchange_to = relationship("Exchange", foreign_keys=[exchange_to_id])


class FlowMetric(Base):
    __tablename__ = "flow_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time_bucket = Column(DateTime, nullable=False, index=True)
    window = Column(String(10), nullable=False)  # "1h", "1d"
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=True, index=True)
    asset_symbol = Column(String(50), nullable=False, index=True)
    inflow = Column(Numeric(36, 18), default=0, nullable=False)
    outflow = Column(Numeric(36, 18), default=0, nullable=False)
    netflow = Column(Numeric(36, 18), default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    exchange = relationship("Exchange")


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=True)
    asset_symbol = Column(String(50), nullable=False)
    window = Column(String(10), nullable=False)
    z_score = Column(Numeric(10, 4), nullable=False)
    netflow = Column(Numeric(36, 18), nullable=False)
    baseline_mean = Column(Numeric(36, 18), nullable=False)
    baseline_std = Column(Numeric(36, 18), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    exchange = relationship("Exchange")
