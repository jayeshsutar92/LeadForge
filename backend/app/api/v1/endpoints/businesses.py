from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.business_contact import BusinessContact
from app.models.user import User
from app.schemas.business import BusinessCard, BusinessDetail, BusinessListResponse
from app.schemas.business_contact import BusinessContactCreate, BusinessContactOut, BusinessContactUpdate
from app.schemas.business_create_update import BusinessCreate, BusinessUpdate
from app.schemas.proposal import ProposalResponse
from app.services.business_contact_service import BusinessContactService
from app.services.business_intelligence_service import BusinessIntelligenceService
from app.services.business_service import BusinessService
from app.services.proposal_service import ProposalService
from app.services.scoring import compute_opportunity_score, get_recommendation
from app.schemas.business_intelligence import BusinessIntelligenceListResponse, BusinessIntelligenceResult

router = APIRouter()


# ─── Business List / Search ───────────────────────────────────────────────────

@router.get("", response_model=BusinessListResponse)
async def list_businesses(
    q: Optional[str] = Query(None, description="Free text query"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    website_status: Optional[str] = Query(None, pattern="^(has|missing)$"),
    min_followers: Optional[int] = 0,
    min_score: Optional[int] = 0,
    sort: str = Query("score_desc", pattern="^(score_desc|followers_desc|name_asc)$"),
    limit: int = Query(60, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    total, cards = await service.list_businesses(
        q=q,
        category=category,
        city=city,
        website_status=website_status,
        min_followers=min_followers or 0,
        min_score=min_score or 0,
        sort=sort,
        limit=limit,
        user_id=str(user.id),
    )
    return BusinessListResponse(total=total, results=cards)


@router.get("/categories")
async def list_categories(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    cats = await service.business_repo.get_categories()
    return {"categories": cats}


@router.get("/stats")
async def platform_stats(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    total = await service.business_repo.count_total()
    missing = await service.business_repo.count_missing_website()

    # Load up to 500 to compute average and top leads
    _, docs = await service.list_businesses(limit=500)
    high = sum(1 for d in docs if d.opportunity_score >= 75)
    avg_score = int(sum(d.opportunity_score for d in docs) / max(1, len(docs)))

    by_cat: dict[str, int] = {}
    for d in docs:
        by_cat[d.category] = by_cat.get(d.category, 0) + 1

    top_leads = docs[:5]

    return {
        "total_businesses": total,
        "missing_website": missing,
        "high_opportunity": high,
        "avg_score": avg_score,
        "by_category": by_cat,
        "top_leads": top_leads,
    }


# ─── Business Detail ──────────────────────────────────────────────────────────

@router.get("/{slug}", response_model=BusinessDetail)
async def get_business(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    b = await service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    card = service._to_card(b)
    b_dict = {
        "name": b.name,
        "category": b.category,
        "city": b.city,
        "country": b.country,
        "followers": b.followers,
        "engagement_rate": b.engagement_rate,
        "website": b.website,
        "instagram": b.instagram,
        "facebook": b.facebook,
        "cover_image": b.cover_image,
        "bio": b.bio,
    }

    return BusinessDetail(
        business=card,
        detail={
            "phone": b.phone,
            "has_online_orders": b.has_online_orders,
            "posts_last_30": b.posts_last_30,
        },
        recommendation=get_recommendation(b_dict),
    )


# ─── Business Intelligence ────────────────────────────────────────────────────

@router.get("/{slug}/intelligence", response_model=BusinessIntelligenceListResponse)
async def list_intelligence(
    slug: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessIntelligenceService(session)
    history = await service.list_history(slug, limit=limit, offset=offset)
    total = await service.count_history(slug)
    
    results = []
    for h in history:
        results.append({
            "id": str(h.id),
            "business_id": str(h.business_id),
            "analysis_type": h.analysis_type,
            "created_at": h.created_at.isoformat(),
            "data": h.data,
        })
    return BusinessIntelligenceListResponse(total=total, results=results)


@router.get("/{slug}/intelligence/latest", response_model=BusinessIntelligenceResult)
async def get_latest_intelligence(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
        
    service = BusinessIntelligenceService(session)
    result = await service.get_latest(b.id)
    if not result:
        raise HTTPException(status_code=404, detail="No intelligence data found")
        
    return BusinessIntelligenceResult.model_validate({
        "id": str(result.id),
        "business_id": str(result.business_id),
        "analysis_type": result.analysis_type,
        "created_at": result.created_at.isoformat(),
        "data": result.data,
    })


@router.post("/{slug}/intelligence/analyze", response_model=BusinessIntelligenceResult)
async def trigger_analysis(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessIntelligenceService(session)
    result = await service.trigger_analysis(slug)
    
    return BusinessIntelligenceResult.model_validate({
        "id": str(result.id),
        "business_id": str(result.business_id),
        "analysis_type": result.analysis_type,
        "created_at": result.created_at.isoformat(),
        "data": result.data,
    })


# ─── Proposal ─────────────────────────────────────────────────────────────────

@router.get("/{slug}/proposal", response_model=ProposalResponse)
async def get_proposal(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    b = await service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    # Build a business dict for the scoring engine and generate a proposal
    # directly from the business data (deterministic, no BI/opportunity dependency)
    b_dict = {
        "name": b.name,
        "category": b.category,
        "city": b.city,
        "country": b.country,
        "followers": b.followers,
        "engagement_rate": b.engagement_rate,
        "website": b.website,
        "instagram": b.instagram,
        "facebook": b.facebook,
        "cover_image": b.cover_image,
        "bio": b.bio,
        "has_online_orders": b.has_online_orders,
        "posts_last_30": b.posts_last_30,
    }

    proposal_service = ProposalService(session)
    content = await proposal_service.generate_content(b_dict)

    return ProposalResponse(
        id=str(b.id),
        opportunity_id=str(b.id),
        version=1,
        content=content,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


# ─── Business CRUD ────────────────────────────────────────────────────────────

@router.post("/", response_model=BusinessCard)
async def create_business(
    payload: BusinessCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    return await service.create_business(payload)


@router.put("/{slug}", response_model=BusinessCard)
async def update_business(
    slug: str,
    payload: BusinessUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    return await service.update_business(slug, payload)


@router.delete("/{slug}", status_code=204)
async def delete_business(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    await service.delete_business(slug)
    return


# ─── Business Contacts ────────────────────────────────────────────────────────

@router.get("/{slug}/contacts", response_model=list[BusinessContactOut])
async def list_contacts(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    contact_service = BusinessContactService(session)
    contacts = await contact_service.list_contacts(b.id)
    return [BusinessContactOut.model_validate(c, from_attributes=True) for c in contacts]


@router.post("/{slug}/contacts", response_model=BusinessContactOut, status_code=201)
async def create_contact(
    slug: str,
    payload: BusinessContactCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    contact = BusinessContact(
        business_id=b.id,
        slug=payload.slug,
        name=payload.name,
        title=payload.title,
        email=payload.email,
        phone=payload.phone,
        notes=payload.notes,
    )
    contact_service = BusinessContactService(session)
    created = await contact_service.create_contact(contact)
    return BusinessContactOut.model_validate(created, from_attributes=True)


@router.put("/{slug}/contacts/{contact_id}", response_model=BusinessContactOut)
async def update_contact(
    slug: str,
    contact_id: UUID,
    payload: BusinessContactUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    contact_service = BusinessContactService(session)
    existing = await contact_service.get_contact(contact_id)
    if not existing or existing.business_id != b.id:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        return BusinessContactOut.model_validate(existing, from_attributes=True)

    updated = await contact_service.update_contact(contact_id, **update_data)
    return BusinessContactOut.model_validate(updated, from_attributes=True)


@router.delete("/{slug}/contacts/{contact_id}", status_code=204)
async def delete_contact(
    slug: str,
    contact_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    contact_service = BusinessContactService(session)
    existing = await contact_service.get_contact(contact_id)
    if not existing or existing.business_id != b.id:
        raise HTTPException(status_code=404, detail="Contact not found")

    await contact_service.delete_contact(contact_id)
    return
