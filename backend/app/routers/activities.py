from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import Activity, User
from app.schemas.schemas import ActivityResponse, ActivityCreate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ActivityResponse])
async def get_activities(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[str] = None,
    lead_id: Optional[str] = None
):
    query = select(Activity)
    
    if customer_id:
        query = query.where(Activity.customer_id == customer_id)
    if lead_id:
        query = query.where(Activity.lead_id == lead_id)
        
    query = query.offset(skip).limit(limit).order_by(desc(Activity.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity_in: ActivityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    activity = Activity(
        **activity_in.model_dump(),
        user_id=current_user.id
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity
