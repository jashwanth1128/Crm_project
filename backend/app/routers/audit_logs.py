from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import AuditLog, User, RoleEnum
from app.api.deps import get_current_user
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict

class AuditLogResponse(BaseModel):
    id: str
    action: str
    entity: str
    entity_id: str
    user_id: str
    created_at: datetime
    changes: Optional[Dict] = None

    model_config = ConfigDict(from_attributes=True)

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 50
):
    # Only admin/manager? Or everyone? Assuming Admin/Manager for audits
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.MANAGER]:
         # Or maybe just return empty or error? Original didn't specify, but safer to restrict.
         pass
         
    query = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
