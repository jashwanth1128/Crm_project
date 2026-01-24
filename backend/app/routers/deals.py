from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import Deal, User, Account, DealStage, Contact
from app.schemas.schemas import DealCreate, DealUpdate, DealResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=DealResponse)
async def create_deal(
    deal_in: DealCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Check Account
    result = await db.execute(select(Account).where(Account.id == deal_in.account_id))
    if not result.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Account not found")

    deal = Deal(
        **deal_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal

@router.get("/", response_model=List[DealResponse])
async def get_deals(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    stage: Optional[DealStage] = None,
    account_id: Optional[str] = None
):
    query = select(Deal)
    if stage:
        query = query.where(Deal.stage == stage)
    if account_id:
        query = query.where(Deal.account_id == account_id)
        
    query = query.order_by(desc(Deal.created_at))
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: str,
    deal_in: DealUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    update_data = deal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)
        
    await db.commit()
    await db.refresh(deal)
    return deal

@router.delete("/{deal_id}")
async def delete_deal(
    deal_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    await db.delete(deal)
    await db.commit()
    return {"message": "Deal deleted"}
