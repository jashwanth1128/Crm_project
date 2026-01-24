from typing import Annotated, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc, func
from app.db.session import get_db
from app.db.models import Lead, LeadStatus, User, RoleEnum, Account, Contact, Deal, DealStage
from app.schemas.schemas import LeadResponse, LeadCreate, LeadUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[LeadStatus] = None
):
    query = select(Lead)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Lead.first_name.ilike(search_filter),
                Lead.last_name.ilike(search_filter),
                Lead.company.ilike(search_filter),
                Lead.email.ilike(search_filter)
            )
        )
    
    if status:
        query = query.where(Lead.status == status)
        
    query = query.offset(skip).limit(limit).order_by(desc(Lead.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_in: LeadCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    lead = Lead(
        **lead_in.model_dump(),
        created_by_id=current_user.id
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_in: LeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    update_data = lead_in.model_dump(exclude_unset=True)
    
    # Status conversion logic
    if update_data.get("status") == LeadStatus.CONVERTED and lead.status != LeadStatus.CONVERTED:
        update_data["converted_at"] = datetime.now(timezone.utc)
        
    for field, value in update_data.items():
        setattr(lead, field, value)
        
    lead.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(lead)
    return lead

@router.post("/{lead_id}/convert")
async def convert_lead(
    lead_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # 1. Fetch Lead
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if lead.status == LeadStatus.CONVERTED:
         # Optionally just return success if already converted
        raise HTTPException(status_code=400, detail="Lead already converted")
        
    # 2. Create Account
    account = Account(
        name=lead.company,
        created_by_id=current_user.id
    )
    db.add(account)
    # Flush to get ID
    await db.flush()
    message = "Created Account"

    # 3. Create Contact
    contact = Contact(
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        title=lead.title,
        account_id=account.id, # Link via ID
        owner_id=current_user.id
    )
    db.add(contact)
    message += ", Contact"

    # 4. Create Deal
    deal = Deal(
        name=f"{lead.company} - {lead.last_name} Deal",
        amount=lead.value,
        stage=DealStage.QUALIFICATION,
        account_id=account.id,
        owner_id=current_user.id
    )
    db.add(deal)
    message += ", Deal"

    # 5. Update Lead
    lead.status = LeadStatus.CONVERTED
    lead.converted_at = datetime.now(timezone.utc)
    lead.converted_account_id = account.id
    
    await db.commit()
    await db.refresh(lead)
    
    return {"message": f"Lead converted successfully. {message}", "account_id": account.id, "deal_id": deal.id}

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
         raise HTTPException(status_code=403, detail="Insufficient permissions")
         
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    await db.delete(lead)
    await db.commit()
    return {"message": "Lead deleted successfully"}

@router.get("/stats/overview")
async def get_lead_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Group by status
    stmt = select(Lead.status, func.count(Lead.id).label("count"), func.sum(Lead.value).label("total_value")).group_by(Lead.status)
    result = await db.execute(stmt)
    
    stats = []
    for row in result:
        stats.append({
            "_id": row.status, 
            "count": row.count,
            "total_value": row.total_value or 0
        })
        
    return {"stats": stats}
