from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import Contact, User, Account
from app.schemas.schemas import ContactCreate, ContactUpdate, ContactResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_in: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Verify account exists if provided
    if contact_in.account_id:
        result = await db.execute(select(Account).where(Account.id == contact_in.account_id))
        account = result.scalar_one_or_none()
        if not account:
             raise HTTPException(status_code=400, detail="Account not found")

    contact = Contact(
        **contact_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    account_id: Optional[str] = None,
    limit: int = 100
):
    query = select(Contact)
    if account_id:
        query = query.where(Contact.account_id == account_id)
        
    query = query.order_by(desc(Contact.created_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_in: ContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = contact_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.commit()
    await db.refresh(contact)
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    await db.delete(contact)
    await db.commit()
    return {"message": "Contact deleted"}
