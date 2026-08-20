import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.repositories.business import BusinessRepository
from app.repositories.social_intelligence import SocialIntelligenceRepository

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{business_id}")
async def get_social_intelligence(
    business_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_id(business_id, user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    si_repo = SocialIntelligenceRepository(session)
    si = await si_repo.get_by_business_id(business_id)
    
    if not si:
        return {"data": None}
        
    return {"data": si.data, "created_at": si.created_at}
