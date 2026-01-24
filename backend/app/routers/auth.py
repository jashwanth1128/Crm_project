from typing import Annotated
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import User, UserStatus
from app.schemas.schemas import Token, LoginRequest, UserCreate, VerifyEmailRequest, UserResponse
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
import uuid
import random
import string
from app.api.deps import get_current_user

router = APIRouter()

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@router.post("/register", response_model=Token)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    otp = generate_otp()
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role,
        status=UserStatus.INACTIVE, # Require verification
        otp=otp,
        is_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # TODO: Send Email (mocked for now as per original server.py mostly)
    print(f"DEBUG: Sent OTP {otp} to {user.email}")
    
    # We return a token even if not verified yet? ORIGINAL logic did not return token but logic suggests we might want them to login to verify.
    # ORIGINAL returned: access_token: "", user data.
    # Let's clean this up. We'll return the user info but maybe no token or a temp token?
    # For simplicity and "fix" -> I will return the user but empty token as original did.
    
    return Token(
        access_token="",
        token_type="bearer",
        user=user
    )

@router.post("/verify-email", response_model=Token)
async def verify_email(
    verify_in: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(User).where(User.email == verify_in.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.otp != verify_in.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    user.status = UserStatus.ACTIVE
    user.is_verified = True
    user.otp = None
    
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token({"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

@router.post("/login", response_model=Token)
async def login(
    login_in: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if user.status != UserStatus.ACTIVE:
         raise HTTPException(status_code=401, detail="Account is not active")
         
    # Update last seen
    user.last_seen = datetime.now(timezone.utc)
    user.is_online = True
    await db.commit()
    
    access_token = create_access_token({"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
