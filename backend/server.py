from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import json
from enum import Enum
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
import random
import string

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", "replace_me"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", "replace_me"),
    MAIL_FROM=os.environ.get("MAIL_USERNAME", "noreply@crm.com"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: EmailStr, otp: str):
    message = MessageSchema(
        subject="CRM - Verify your email",
        recipients=[email],
        body=f"Your verification code is: {otp}",
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_DAYS = 7
security = HTTPBearer()

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", "replace_me"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", "replace_me"),
    MAIL_FROM=os.environ.get("MAIL_USERNAME", "noreply@crm.com"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: EmailStr, otp: str):
    message = MessageSchema(
        subject="CRM - Verify your email",
        recipients=[email],
        body=f"Your verification code is: {otp}",
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", "replace_me"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", "replace_me"),
    MAIL_FROM=os.environ.get("MAIL_USERNAME", "noreply@crm.com"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: EmailStr, otp: str):
    message = MessageSchema(
        subject="CRM - Verify your email",
        recipients=[email],
        body=f"Your verification code is: {otp}",
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except:
                self.disconnect(user_id)

    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        disconnected = []
        for user_id, connection in self.active_connections.items():
            if user_id != exclude_user:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(user_id)
        for user_id in disconnected:
            self.disconnect(user_id)

manager = ConnectionManager()

# Enums
class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class CustomerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CHURNED = "CHURNED"

class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CONVERTED = "CONVERTED"
    LOST = "LOST"

class LeadSource(str, Enum):
    WEBSITE = "WEBSITE"
    REFERRAL = "REFERRAL"
    COLD_CALL = "COLD_CALL"
    EMAIL = "EMAIL"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    OTHER = "OTHER"

class ActivityType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"
    TASK = "TASK"

class NotificationType(str, Enum):
    LEAD_UPDATED = "LEAD_UPDATED"
    LEAD_ASSIGNED = "LEAD_ASSIGNED"
    CUSTOMER_ASSIGNED = "CUSTOMER_ASSIGNED"
    ACTIVITY_ADDED = "ACTIVITY_ADDED"
    MENTION = "MENTION"
    SYSTEM = "SYSTEM"

# Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleEnum = RoleEnum.EMPLOYEE
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    dark_mode: Optional[bool] = None
    role: Optional[RoleEnum] = None
    status: Optional[UserStatus] = None

class User(UserBase):
    id: str
    status: UserStatus = UserStatus.ACTIVE
    is_online: bool = False
    last_seen: datetime
    dark_mode: bool = False
    created_at: datetime
    created_at: datetime
    updated_at: datetime
    is_verified: bool = False
    otp: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    status: CustomerStatus = CustomerStatus.ACTIVE
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    status: Optional[CustomerStatus] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

class Customer(CustomerBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

class LeadBase(BaseModel):
    title: str
    description: Optional[str] = None
    value: Optional[float] = None
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource = LeadSource.OTHER
    customer_id: str
    assigned_to: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    customer_id: Optional[str] = None
    assigned_to: Optional[str] = None

class Lead(LeadBase):
    id: str
    created_by: str
    converted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ActivityBase(BaseModel):
    type: ActivityType
    subject: str
    description: Optional[str] = None
    duration: Optional[int] = None
    customer_id: Optional[str] = None
    lead_id: Optional[str] = None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class Notification(BaseModel):
    id: str
    type: NotificationType
    title: str
    message: str
    is_read: bool = False
    user_id: str
    metadata: Optional[Dict] = None
    created_at: datetime

class AuditLog(BaseModel):
    id: str
    action: str
    entity: str
    entity_id: str
    changes: Optional[Dict] = None
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise credentials_exception
    return user

async def create_audit_log(action: str, entity: str, entity_id: str, user_id: str, changes: Optional[dict] = None):
    log = {
        "id": str(uuid.uuid4()),
        "action": action,
        "entity": entity,
        "entity_id": entity_id,
        "changes": changes,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.audit_logs.insert_one(log)

async def create_notification(user_id: str, type: NotificationType, title: str, message: str, metadata: Optional[dict] = None):
    notification = {
        "id": str(uuid.uuid4()),
        "type": type.value,
        "title": title,
        "message": message,
        "is_read": False,
        "user_id": user_id,
        "metadata": metadata,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    try:
        await manager.send_personal_message({"type": "notification", "data": notification}, user_id)
    except:
        pass

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_dict = user_data.model_dump()
    
    # Hash password
    hashed_password = get_password_hash(user_dict["password"])
    user_dict["password"] = hashed_password
    
    # Add metadata
    user_dict["id"] = str(uuid.uuid4())
    user_dict["status"] = UserStatus.INACTIVE # Default to INACTIVE until verified
    user_dict["is_online"] = False
    
    # Generate OTP
    otp = generate_otp()
    user_dict["otp"] = otp
    user_dict["is_verified"] = False
    
    user_dict["last_seen"] = datetime.now(timezone.utc).isoformat()
    user_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    user_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Insert user
    await db.users.insert_one(user_dict)
    
    # Send OTP
    try:
        await send_verification_email(user_data.email, otp)
    except Exception as e:
        print(f"Failed to send email: {e}")
        # Ideally rollback or allow retry, but for now we proceed
    
    return {
        "access_token": "", # No token yet
        "token_type": "bearer", 
        "user": {
            "id": user_dict["id"],
            "email": user_dict["email"],
            "first_name": user_dict["first_name"],
            "last_name": user_dict["last_name"],
            "role": user_dict["role"],
            "status": user_dict["status"],
            "is_verified": False,
            "created_at": datetime.fromisoformat(user_dict["created_at"]),
            "updated_at": datetime.fromisoformat(user_dict["created_at"]),
            "last_seen": datetime.fromisoformat(user_dict["last_seen"])
        }
    }

@api_router.post("/auth/verify-email", response_model=Token)
async def verify_email(verify_data: VerifyEmailRequest):
    user = await db.users.find_one({"email": verify_data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.get("otp") != verify_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # Activate user
    await db.users.update_one(
        {"email": verify_data.email},
        {"$set": {"status": UserStatus.ACTIVE, "is_verified": True, "otp": None}}
    )
    
    # Login (Create token)
    access_token = create_access_token({"sub": user["id"]})
    
    # Prepare response
    user_response = {k: v for k, v in user.items() if k != "password" and k != "otp"}
    user_response["status"] = UserStatus.ACTIVE
    user_response["last_seen"] = datetime.fromisoformat(user_response["last_seen"])
    user_response["created_at"] = datetime.fromisoformat(user_response["created_at"])
    user_response["updated_at"] = datetime.fromisoformat(user_response["updated_at"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }
@api_router.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if user["status"] != UserStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Account is not active")

    
    # Update last seen
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_seen": datetime.now(timezone.utc).isoformat(), "is_online": True}}
    )
    
    # Create token
    access_token = create_access_token({"sub": user["id"]})
    
    # Remove password from response
    user.pop("password")
    user["last_seen"] = datetime.fromisoformat(user["last_seen"])
    user["created_at"] = datetime.fromisoformat(user["created_at"])
    user["updated_at"] = datetime.fromisoformat(user["updated_at"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    current_user["last_seen"] = datetime.fromisoformat(current_user["last_seen"])
    current_user["created_at"] = datetime.fromisoformat(current_user["created_at"])
    current_user["updated_at"] = datetime.fromisoformat(current_user["updated_at"])
    return current_user

# User routes
@api_router.get("/users", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    for user in users:
        user["last_seen"] = datetime.fromisoformat(user["last_seen"])
        user["created_at"] = datetime.fromisoformat(user["created_at"])
        user["updated_at"] = datetime.fromisoformat(user["updated_at"])
    return users

@api_router.patch("/users/{user_id}", response_model=User)
async def update_user(user_id: str, update_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    # Only admin can update others, users can update themselves
    if current_user["role"] != RoleEnum.ADMIN and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await create_audit_log("UPDATE", "User", user_id, current_user["id"], update_dict)
    
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    updated_user["last_seen"] = datetime.fromisoformat(updated_user["last_seen"])
    updated_user["created_at"] = datetime.fromisoformat(updated_user["created_at"])
    updated_user["updated_at"] = datetime.fromisoformat(updated_user["updated_at"])
    return updated_user

# Customer routes
@api_router.get("/customers", response_model=List[Customer])
async def get_customers(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[CustomerStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}}
        ]
    if status:
        query["status"] = status
    
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    for customer in customers:
        customer["created_at"] = datetime.fromisoformat(customer["created_at"])
        customer["updated_at"] = datetime.fromisoformat(customer["updated_at"])
    return customers

@api_router.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, current_user: dict = Depends(get_current_user)):
    customer_dict = customer_data.model_dump()
    customer_dict["id"] = str(uuid.uuid4())
    customer_dict["created_by"] = current_user["id"]
    customer_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    customer_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.customers.insert_one(customer_dict)
    await create_audit_log("CREATE", "Customer", customer_dict["id"], current_user["id"])
    
    # Notify assigned user
    if customer_dict.get("assigned_to"):
        await create_notification(
            customer_dict["assigned_to"],
            NotificationType.CUSTOMER_ASSIGNED,
            "New Customer Assigned",
            f"You have been assigned customer: {customer_dict['name']}",
            {"customer_id": customer_dict["id"]}
        )
    
    # Broadcast to all users
    await manager.broadcast({"type": "customer_created", "data": customer_dict})
    
    customer_dict["created_at"] = datetime.fromisoformat(customer_dict["created_at"])
    customer_dict["updated_at"] = datetime.fromisoformat(customer_dict["updated_at"])
    return customer_dict

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer["created_at"] = datetime.fromisoformat(customer["created_at"])
    customer["updated_at"] = datetime.fromisoformat(customer["updated_at"])
    return customer

@api_router.patch("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, update_data: CustomerUpdate, current_user: dict = Depends(get_current_user)):
    update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.customers.update_one({"id": customer_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await create_audit_log("UPDATE", "Customer", customer_id, current_user["id"], update_dict)
    
    updated_customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    
    # Broadcast update
    await manager.broadcast({"type": "customer_updated", "data": updated_customer})
    
    updated_customer["created_at"] = datetime.fromisoformat(updated_customer["created_at"])
    updated_customer["updated_at"] = datetime.fromisoformat(updated_customer["updated_at"])
    return updated_customer

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await create_audit_log("DELETE", "Customer", customer_id, current_user["id"])
    await manager.broadcast({"type": "customer_deleted", "data": {"id": customer_id}})
    
    return {"message": "Customer deleted successfully"}

# Lead routes
@api_router.get("/leads", response_model=List[Lead])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[LeadStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if status:
        query["status"] = status
    
    leads = await db.leads.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    for lead in leads:
        lead["created_at"] = datetime.fromisoformat(lead["created_at"])
        lead["updated_at"] = datetime.fromisoformat(lead["updated_at"])
        if lead.get("converted_at"):
            lead["converted_at"] = datetime.fromisoformat(lead["converted_at"])
    return leads

@api_router.post("/leads", response_model=Lead)
async def create_lead(lead_data: LeadCreate, current_user: dict = Depends(get_current_user)):
    lead_dict = lead_data.model_dump()
    lead_dict["id"] = str(uuid.uuid4())
    lead_dict["created_by"] = current_user["id"]
    lead_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    lead_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    lead_dict["converted_at"] = None
    
    await db.leads.insert_one(lead_dict)
    await create_audit_log("CREATE", "Lead", lead_dict["id"], current_user["id"])
    
    # Notify assigned user
    if lead_dict.get("assigned_to"):
        await create_notification(
            lead_dict["assigned_to"],
            NotificationType.LEAD_ASSIGNED,
            "New Lead Assigned",
            f"You have been assigned lead: {lead_dict['title']}",
            {"lead_id": lead_dict["id"]}
        )
    
    # Broadcast to all users
    await manager.broadcast({"type": "lead_created", "data": lead_dict})
    
    lead_dict["created_at"] = datetime.fromisoformat(lead_dict["created_at"])
    lead_dict["updated_at"] = datetime.fromisoformat(lead_dict["updated_at"])
    return lead_dict

@api_router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead["created_at"] = datetime.fromisoformat(lead["created_at"])
    lead["updated_at"] = datetime.fromisoformat(lead["updated_at"])
    if lead.get("converted_at"):
        lead["converted_at"] = datetime.fromisoformat(lead["converted_at"])
    return lead

@api_router.patch("/leads/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, update_data: LeadUpdate, current_user: dict = Depends(get_current_user)):
    update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # If status changed to CONVERTED, set converted_at
    if update_dict.get("status") == LeadStatus.CONVERTED:
        update_dict["converted_at"] = datetime.now(timezone.utc).isoformat()
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.leads.update_one({"id": lead_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    await create_audit_log("UPDATE", "Lead", lead_id, current_user["id"], update_dict)
    
    updated_lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    
    # Notify if status changed
    if update_dict.get("status") and updated_lead.get("assigned_to"):
        await create_notification(
            updated_lead["assigned_to"],
            NotificationType.LEAD_UPDATED,
            "Lead Status Updated",
            f"Lead '{updated_lead['title']}' status changed to {update_dict['status']}",
            {"lead_id": lead_id}
        )
    
    # Broadcast update
    await manager.broadcast({"type": "lead_updated", "data": updated_lead})
    
    updated_lead["created_at"] = datetime.fromisoformat(updated_lead["created_at"])
    updated_lead["updated_at"] = datetime.fromisoformat(updated_lead["updated_at"])
    if updated_lead.get("converted_at"):
        updated_lead["converted_at"] = datetime.fromisoformat(updated_lead["converted_at"])
    return updated_lead

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    await create_audit_log("DELETE", "Lead", lead_id, current_user["id"])
    await manager.broadcast({"type": "lead_deleted", "data": {"id": lead_id}})
    
    return {"message": "Lead deleted successfully"}

@api_router.get("/leads/stats/overview")
async def get_lead_stats(current_user: dict = Depends(get_current_user)):
    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_value": {"$sum": "$value"}
        }}
    ]
    stats = await db.leads.aggregate(pipeline).to_list(100)
    return {"stats": stats}

# Activity routes
@api_router.get("/activities", response_model=List[Activity])
async def get_activities(
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[str] = None,
    lead_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    if lead_id:
        query["lead_id"] = lead_id
    
    activities = await db.activities.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for activity in activities:
        activity["created_at"] = datetime.fromisoformat(activity["created_at"])
        activity["updated_at"] = datetime.fromisoformat(activity["updated_at"])
    return activities

@api_router.post("/activities", response_model=Activity)
async def create_activity(activity_data: ActivityCreate, current_user: dict = Depends(get_current_user)):
    activity_dict = activity_data.model_dump()
    activity_dict["id"] = str(uuid.uuid4())
    activity_dict["user_id"] = current_user["id"]
    activity_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    activity_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.activities.insert_one(activity_dict)
    await create_audit_log("CREATE", "Activity", activity_dict["id"], current_user["id"])
    
    # Broadcast to all users
    await manager.broadcast({"type": "activity_created", "data": activity_dict})
    
    activity_dict["created_at"] = datetime.fromisoformat(activity_dict["created_at"])
    activity_dict["updated_at"] = datetime.fromisoformat(activity_dict["updated_at"])
    return activity_dict

# Notification routes
@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    query = {"user_id": current_user["id"]}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for notification in notifications:
        notification["created_at"] = datetime.fromisoformat(notification["created_at"])
    return notifications

@api_router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"is_read": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@api_router.post("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user["id"], "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"message": "All notifications marked as read"}

# Audit log routes (Admin only)
@api_router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    # Check if user is admin
    if current_user["role"] != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    logs = await db.audit_logs.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for log in logs:
        log["created_at"] = datetime.fromisoformat(log["created_at"])
    return logs

# WebSocket endpoint
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return
    
    # Connect user
    await manager.connect(user_id, websocket)
    
    # Update user status to online
    await db.users.update_one({"id": user_id}, {"$set": {"is_online": True}})
    await manager.broadcast({"type": "user_online", "data": {"user_id": user_id}})
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"is_online": False, "last_seen": datetime.now(timezone.utc).isoformat()}}
        )
        await manager.broadcast({"type": "user_offline", "data": {"user_id": user_id}})

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup event
@app.on_event("startup")
async def startup_event():
    # Create default admin user
    admin_email = "admin@crm.com"
    admin = await db.users.find_one({"email": admin_email})
    if not admin:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password": get_password_hash("admin123"),
            "first_name": "Admin",
            "last_name": "User",
            "role": RoleEnum.ADMIN,
            "status": UserStatus.ACTIVE,
            "is_online": False,
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "dark_mode": False,
            "avatar": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_user)
        logger.info(f"Default admin user created: {admin_email} / admin123")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
