from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.business import BusinessCard, BusinessDetail, BusinessListResponse, ProposalResponse
from app.schemas.business_create_update import BusinessCreate, BusinessUpdate
from app.services.business_service import BusinessService
from app.services.proposal_service import ProposalService
from app.services.scoring import compute_opportunity_score, get_recommendation
from app.repositories.opportunity import OpportunityRepository

router = APIRouter()


@router.get("", response_model=BusinessListResponse)
async def list_businesses(
    q: Optional[str] = Query(None, description="Free text query"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    website_status: Optional[str] = Query(None, pattern="^(has|missing)$"),
    min_followers: Optional[int] = 0,
    min_score: Optional[int] = 0,
    sort: str = Query("score_desc", pattern="^(score_desc|followers_desc|name_asc)$"),
    limit: int = Query(60, ge=1, le=200),
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
        user_id=str(user.id)
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
    
    # We load 500 max to compute average and top leads
    _, docs = await service.list_businesses(limit=500)
    high = sum(1 for d in docs if d.opportunity_score >= 75)
    avg_score = int(sum(d.opportunity_score for d in docs) / max(1, len(docs)))
    
    by_cat = {}
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
    # create dict representation for get_recommendation
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

    # Retrieve the latest opportunity for this business
    opp_repo = OpportunityRepository(session)
    opportunity = await opp_repo.get_latest_by_business_intelligence(str(b.id))
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    proposal_service = ProposalService(session)
    proposal = await proposal_service.get_or_create_proposal(opportunity.id, opportunity.data)
    return proposal


# CRUD endpoints for Business

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
