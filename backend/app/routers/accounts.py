from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import Account, User
from app.schemas.schemas import AccountCreate, AccountUpdate, AccountResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=AccountResponse)
async def create_account(
    account_in: AccountCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    account = Account(
        **account_in.model_dump(),
        created_by_id=current_user.id
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
):
    query = select(Account).offset(skip).limit(limit).order_by(desc(Account.created_at))
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    account_in: AccountUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = account_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    await db.commit()
    await db.refresh(account)
    return account

@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    await db.delete(account)
    await db.commit()
    return {"message": "Account deleted successfully"}
