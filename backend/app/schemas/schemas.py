from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from app.db.models import RoleEnum, UserStatus, LeadStatus, DealStage

# --- Token ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Any # Avoid circular dependency, simplify for now

class TokenData(BaseModel):
    username: Optional[str] = None

# --- User ---
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: RoleEnum = RoleEnum.EMPLOYEE

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

class UserResponse(UserBase):
    id: str
    status: UserStatus
    is_verified: bool
    avatar: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

# --- Account (was Customer) ---
class AccountBase(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    billing_address: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(AccountBase):
    name: Optional[str] = None

class AccountResponse(AccountBase):
    id: str
    created_by_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Contact ---
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    account_id: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ContactResponse(ContactBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Deal ---
class DealBase(BaseModel):
    name: str
    amount: float = 0.0
    stage: DealStage = DealStage.QUALIFICATION
    closing_date: Optional[datetime] = None
    account_id: str
    contact_id: Optional[str] = None

class DealCreate(DealBase):
    pass

class DealUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    stage: Optional[DealStage] = None
    closing_date: Optional[datetime] = None
    probability: Optional[int] = None

class DealResponse(DealBase):
    id: str
    probability: int
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Lead ---
class LeadBase(BaseModel):
    first_name: str
    last_name: str
    company: str
    email: EmailStr
    title: Optional[str] = None
    source: Optional[str] = None
    value: float = 0.0
    status: LeadStatus = LeadStatus.NEW

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[LeadStatus] = None
    value: Optional[float] = None

class LeadResponse(LeadBase):
    id: str
    created_by_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Activity ---
class ActivityBase(BaseModel):
    type: str
    subject: str
    description: Optional[str] = None
    account_id: Optional[str] = None
    lead_id: Optional[str] = None
    deal_id: Optional[str] = None

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: str
    user_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Notification ---
class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
