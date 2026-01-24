import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Text, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
import enum

def generate_uuid():
    return str(uuid.uuid4())

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    LOST = "LOST"
    CONVERTED = "CONVERTED"

class DealStage(str, enum.Enum):
    QUALIFICATION = "QUALIFICATION"
    NEEDS_ANALYSIS = "NEEDS_ANALYSIS"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[RoleEnum] = mapped_column(String, default=RoleEnum.EMPLOYEE)
    status: Mapped[UserStatus] = mapped_column(String, default=UserStatus.ACTIVE)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    otp: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    accounts = relationship("Account", back_populates="owner")
    contacts = relationship("Contact", back_populates="owner")
    leads = relationship("Lead", back_populates="owner")
    deals = relationship("Deal", back_populates="owner")
    activities = relationship("Activity", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Account(Base):
    """Replaces 'Customer'. Represents a Company/Organization."""
    __tablename__ = "accounts"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, index=True) # Company Name
    industry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="accounts")
    
    contacts = relationship("Contact", back_populates="account", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="account")
    activities = relationship("Activity", back_populates="account")

class Contact(Base):
    """Represents a Person within an Account."""
    __tablename__ = "contacts"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Job Title
    
    account_id: Mapped[Optional[str]] = mapped_column(ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="contacts")
    
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="contacts")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Lead(Base):
    """Unqualified prospect."""
    __tablename__ = "leads"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    company: Mapped[String] = mapped_column(String)
    email: Mapped[String] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, nullable=True) # Job Title
    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(String, default=LeadStatus.NEW)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="leads")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # When converted, link to the created entities (optional tracking)
    converted_account_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    converted_contact_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    converted_deal_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class Deal(Base):
    """Sales Opportunity."""
    __tablename__ = "deals"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String) # Deal Name
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    stage: Mapped[DealStage] = mapped_column(String, default=DealStage.QUALIFICATION)
    closing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    probability: Mapped[int] = mapped_column(Integer, default=10) # 0-100%
    
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="deals")
    
    contact_id: Mapped[Optional[str]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    # contact relationship if needed
    
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="deals")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Activity(Base):
    __tablename__ = "activities"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    type: Mapped[str] = mapped_column(String) # CALL, MEETING, EMAIL, NOTE
    subject: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="activities")
    
    # Polymorphic-ish association
    account_id: Mapped[Optional[str]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    account = relationship("Account", back_populates="activities")
    
    lead_id: Mapped[Optional[str]] = mapped_column(ForeignKey("leads.id"), nullable=True)
    # lead relationship manual setup if needed in future
    
    deal_id: Mapped[Optional[str]] = mapped_column(ForeignKey("deals.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="notifications")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    action: Mapped[str] = mapped_column(String) # CREATE, UPDATE, DELETE
    entity: Mapped[str] = mapped_column(String) # ACCOUNT, LEAD, DEAL
    entity_id: Mapped[str] = mapped_column(String)
    changes: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON string
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
