from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.crm import ActivityCreate, LeadCreate, LeadDetailResponse, LeadListResponse, LeadResponse, LeadUpdate
from app.schemas.proposal import ProposalSummaryResponse
from app.services.crm_service import CRMService
from app.services.business_service import BusinessService

from sqlalchemy import select
from app.models.proposal import Proposal
from app.models.opportunity import Opportunity
from app.models.business_intelligence import BusinessIntelligence
from app.models.business import Business

router = APIRouter()


# ─── Proposals ────────────────────────────────────────────────────────────────

@router.get("/proposals", response_model=list[ProposalSummaryResponse])
async def list_proposals(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    from app.services.discovery_session_service import DiscoverySessionService
    active_session = await DiscoverySessionService(session).get_active_session(user.id)
    active_session_id = str(active_session.id) if active_session else None

    stmt = (
        select(Proposal, Business.slug)
        .join(Opportunity, Proposal.opportunity_id == Opportunity.id)
        .join(BusinessIntelligence, Opportunity.business_intelligence_id == BusinessIntelligence.id)
        .join(Business, BusinessIntelligence.business_id == Business.id)
        .where(Business.user_id == user.id)
    )
    
    if active_session_id:
        from sqlalchemy import cast, String
        stmt = stmt.where(cast(Business.discovery_session_ids, String).like(f"%{active_session_id}%"))
        
    stmt = stmt.order_by(Proposal.created_at.desc())
    result = await session.execute(stmt)
    rows = result.all()
    
    # Map to schema
    return [
        {
            "slug": slug,
            "proposal": {
                "id": str(prop.id),
                "opportunity_id": str(prop.opportunity_id),
                "version": prop.version,
                "content": prop.content,
                "created_at": prop.created_at,
                "updated_at": prop.updated_at,
            }
        }
        for prop, slug in rows
    ]



# ─── Leads ────────────────────────────────────────────────────────────────────

@router.get("/leads", response_model=LeadListResponse)
async def list_leads(
    q: Optional[str] = Query(None, description="Search term for notes/source"),
    status: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    min_priority: Optional[int] = Query(None, description="1 is high, 3 is low"),
    sort: str = Query("created_desc", description="Sort order"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    from app.services.discovery_session_service import DiscoverySessionService
    active_session = await DiscoverySessionService(session).get_active_session(user.id)
    active_session_id = str(active_session.id) if active_session else None

    service = CRMService(session)
    total, leads = await service.list_leads(
        user_id=user.id,
        q=q,
        status=status,
        assigned_to=assigned_to,
        min_priority=min_priority,
        limit=limit,
        offset=offset,
        sort=sort,
        session_id=active_session_id,
    )
    return LeadListResponse(total=total, results=leads)


@router.post("/leads", response_model=LeadDetailResponse, status_code=201)
async def create_lead(
    payload: LeadCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    # Verify business exists
    biz_service = BusinessService(session)
    biz = await biz_service.business_repo.get_by_id(payload.business_id, user.id)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    service = CRMService(session)
    lead = await service.create_lead(payload, current_user_id=user.id)
    return LeadDetailResponse.model_validate(lead)


@router.get("/leads/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    lead_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = CRMService(session)
    lead = await service.get_lead(lead_id, user.id)
    return LeadDetailResponse.model_validate(lead)


@router.put("/leads/{lead_id}", response_model=LeadDetailResponse)
async def update_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = CRMService(session)
    lead = await service.update_lead(lead_id, payload, current_user_id=user.id)
    return LeadDetailResponse.model_validate(lead)


@router.delete("/leads/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    from app.services.discovery_session_service import DiscoverySessionService
    active_session = await DiscoverySessionService(session).get_active_session(user.id)
    active_session_id = str(active_session.id) if active_session else None

    service = CRMService(session)
    await service.delete_lead(lead_id, user.id, session_id=active_session_id)
    return


# ─── Lead Activities / Workflow ───────────────────────────────────────────────

@router.post("/leads/{lead_id}/activities", response_model=LeadDetailResponse, status_code=201)
async def log_activity(
    lead_id: UUID,
    payload: ActivityCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = CRMService(session)
    lead = await service.log_activity(lead_id, payload, current_user_id=user.id)
    return LeadDetailResponse.model_validate(lead)
