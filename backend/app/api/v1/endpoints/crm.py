from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.crm import ActivityCreate, LeadCreate, LeadDetailResponse, LeadListResponse, LeadResponse, LeadUpdate
from app.services.crm_service import CRMService
from app.services.business_service import BusinessService

router = APIRouter()


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
    service = CRMService(session)
    total, leads = await service.list_leads(
        q=q,
        status=status,
        assigned_to=assigned_to,
        min_priority=min_priority,
        limit=limit,
        offset=offset,
        sort=sort,
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
    biz = await biz_service.business_repo.get_by_id(payload.business_id)
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
    lead = await service.get_lead(lead_id)
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
    service = CRMService(session)
    await service.delete_lead(lead_id)
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
