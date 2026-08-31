from __future__ import annotations

import logging
import re
import httpx
import asyncio
from fastapi import BackgroundTasks
from pydantic import BaseModel, Field
from urllib.parse import quote_plus
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
from app.services.opportunity_service import OpportunityService
from app.services.proposal_service import ProposalService
from app.services.scoring import compute_opportunity_score, get_recommendation
from app.schemas.business_intelligence import BusinessIntelligenceListResponse, BusinessIntelligenceResult
from app.schemas.opportunity import OpportunityResponse
from app.services.crm_service import CRMService
from app.schemas.crm import LeadCreate

logger = logging.getLogger(__name__)

class DiscoverRequest(BaseModel):
    query: str
    region: str

class DiscoverResponse(BaseModel):
    message: str
    found: int
    new_leads: int
    results: list[BusinessCard] = Field(default_factory=list)

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
        user_id=user.id,
    )
    return BusinessListResponse(total=total, results=cards)


@router.post("/discover", response_model=DiscoverResponse)
async def discover_businesses(
    payload: DiscoverRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    # Normalize query and region
    query_normalized = payload.query.strip().lower()
    region_normalized = payload.region.strip().lower()
    query_str = quote_plus(f"{query_normalized} {region_normalized}")
    url = f"https://nominatim.openstreetmap.org/search?q={query_str}&format=json&extratags=1&addressdetails=1&limit=10"
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers={"User-Agent": "LeadForgeBackend/1.0"}, timeout=15.0)
            res.raise_for_status()
            results = res.json()
            logger.info(f"Discovery URL: {url} returned {len(results)} raw results.")
    except Exception as e:
        logger.error(f"Discovery API failed: {e}")
        raise HTTPException(status_code=502, detail="External discovery service failed")

    valid_results = [r for r in results if r.get("name")]
    if not valid_results:
        logger.warning(f"Nominatim returned {results}")
    
    biz_service = BusinessService(session)
    crm_service = CRMService(session)
    bi_service = BusinessIntelligenceService(session)
    
    new_leads = 0
    failed_imports = 0
    discovered_cards = []
    social_intelligence_slugs = []
    
    for place in valid_results:
        try:
            name = place["name"]
            city_slug = region_normalized.replace(' ', '-')
            raw_slug = f"{name.lower().replace(' ', '-').replace('/', '-')}-{city_slug}-{place.get('place_id')}"
            slug = re.sub(r'[^a-z0-9\-]', '', raw_slug)
            
            existing = await biz_service.business_repo.get_by_slug(slug, user.id)
            if existing:
                card = biz_service._to_card(existing)
                if not any(c.id == card.id for c in discovered_cards):
                    discovered_cards.append(card)
                continue
                
            extratags = place.get("extratags") or {}
            address = place.get("address") or {}
            
            website = extratags.get("website") or extratags.get("contact:website") or extratags.get("url") or ""
            city = address.get("city") or address.get("town") or address.get("village") or address.get("county") or payload.region
            country = address.get("country", "Unknown")
            
            biz_create = BusinessCreate(
                name=name,
                slug=slug,
                category=query_normalized,
                city=city,
                country=country,
                website=website,
                bio=f"Discovered via OpenStreetMap. Category: {place.get('type', 'unknown')}"
            )
            
            biz = await biz_service.create_business(biz_create, user.id)
            if any(c.id == biz.id for c in discovered_cards):
                continue
                
            discovered_cards.append(biz)
            
            lead_create = LeadCreate(
                business_id=biz.id,
                source="Discovery Scan",
                notes=f"Discovered scanning for {payload.query} in {payload.region}"
            )
            await crm_service.create_lead(lead_create, current_user_id=user.id)
            # Regular BI analysis
            try:
                await bi_service.trigger_analysis(biz.slug, user.id)
                await asyncio.sleep(1.5) # Prevent rate-limiting on burst discovery
            except Exception as e:
                logger.error(f"Failed to trigger analysis for {biz.slug}: {e}")
                
            # Collect slug for Social Intelligence if website is missing
            if not biz.website:
                social_intelligence_slugs.append(biz.slug)
            
            new_leads += 1
            
        except Exception as e:
            failed_imports += 1
            logger.exception(f"Failed to process discovered business {place.get('name')}: {e}")

    if failed_imports > 0 and failed_imports == len(valid_results):
        raise HTTPException(status_code=500, detail="Failed to import any businesses from discovery due to internal errors.")

    # Trigger Social Intelligence sequentially in a single background task
    if social_intelligence_slugs:
        from app.db.session import AsyncSessionLocal
        from app.services.social_intelligence_service import SocialIntelligenceService
        
        async def run_social_intelligence_batch(slugs: list[str], uid: UUID):
            async with AsyncSessionLocal() as bg_session:
                si_service = SocialIntelligenceService(bg_session)
                for slug in slugs:
                    try:
                        await si_service.trigger_analysis(slug, uid)
                        await asyncio.sleep(2.0)  # Graceful delay between businesses
                    except Exception as e:
                        logger.error(f"Social intelligence task failed for {slug}: {e}")
                        
        background_tasks.add_task(run_social_intelligence_batch, social_intelligence_slugs, user.id)
            
            
    return DiscoverResponse(
        message=f"Found {len(valid_results)} businesses, processed {new_leads} new leads.",
        found=len(valid_results),
        new_leads=new_leads,
        results=discovered_cards
    )


@router.get("/categories")
async def list_categories(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    cats = await service.business_repo.get_categories(user.id)
    return {"categories": cats}


@router.get("/stats")
async def platform_stats(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    total = await service.business_repo.count_total(user.id)
    missing = await service.business_repo.count_missing_website(user.id)

    # Load up to 500 to compute average and top leads
    _, docs = await service.list_businesses(limit=500, user_id=user.id)
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
    b = await service.business_repo.get_by_slug(slug, user.id)
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
    history = await service.list_history(slug, limit=limit, offset=offset, user_id=user.id)
    total = await service.count_history(slug, user_id=user.id)
    
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
    b = await biz_service.business_repo.get_by_slug(slug, user.id)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
        
    service = BusinessIntelligenceService(session)
    result = await service.get_latest(b.id, user_id=user.id)
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
    result = await service.trigger_analysis(slug, user_id=user.id)
    
    return BusinessIntelligenceResult.model_validate({
        "id": str(result.id),
        "business_id": str(result.business_id),
        "analysis_type": result.analysis_type,
        "created_at": result.created_at.isoformat(),
        "data": result.data,
    })


# ─── Opportunity Engine ───────────────────────────────────────────────────────

@router.get("/{slug}/intelligence/{bi_id}/opportunity", response_model=OpportunityResponse)
async def get_opportunity(
    slug: str,
    bi_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug, user.id)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
        
    service = OpportunityService(session)
    result = await service.get_latest(bi_id, user_id=user.id)
    if not result:
        raise HTTPException(status_code=404, detail="No opportunity data found")
        
    return OpportunityResponse.model_validate({
        "id": str(result.id),
        "business_intelligence_id": str(result.business_intelligence_id),
        "created_at": result.created_at,
        "updated_at": result.updated_at,
        "data": result.data,
    })


@router.post("/{slug}/intelligence/{bi_id}/opportunity/generate", response_model=OpportunityResponse)
async def generate_opportunity(
    slug: str,
    bi_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = OpportunityService(session)
    result = await service.generate_opportunity(bi_id, slug, user_id=user.id)
    
    return OpportunityResponse.model_validate({
        "id": str(result.id),
        "business_intelligence_id": str(result.business_intelligence_id),
        "created_at": result.created_at,
        "updated_at": result.updated_at,
        "data": result.data,
    })


# ─── Proposal ─────────────────────────────────────────────────────────────────

@router.get("/{slug}/opportunity/{opportunity_id}/proposal", response_model=ProposalResponse)
async def get_latest_proposal(
    slug: str,
    opportunity_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = ProposalService(session)
    proposal = await service.get_latest(opportunity_id, user_id=user.id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    return ProposalResponse.model_validate({
        "id": str(proposal.id),
        "opportunity_id": str(proposal.opportunity_id),
        "version": proposal.version,
        "content": proposal.content,
        "created_at": proposal.created_at,
        "updated_at": proposal.updated_at,
    })


@router.post("/{slug}/opportunity/{opportunity_id}/proposal/generate", response_model=ProposalResponse)
async def generate_proposal(
    slug: str,
    opportunity_id: UUID,
    template_type: str = Query("standard", description="Template to use (standard, premium, quick_win)"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = ProposalService(session)
    proposal = await service.generate_proposal(opportunity_id, template_type=template_type, user_id=user.id)
    
    return ProposalResponse.model_validate({
        "id": str(proposal.id),
        "opportunity_id": str(proposal.opportunity_id),
        "version": proposal.version,
        "content": proposal.content,
        "created_at": proposal.created_at,
        "updated_at": proposal.updated_at,
    })


@router.put("/{slug}/proposal/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    slug: str,
    proposal_id: UUID,
    content: dict,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = ProposalService(session)
    proposal = await service.update_proposal(proposal_id, content, user_id=user.id)
    
    return ProposalResponse.model_validate({
        "id": str(proposal.id),
        "opportunity_id": str(proposal.opportunity_id),
        "version": proposal.version,
        "content": proposal.content,
        "created_at": proposal.created_at,
        "updated_at": proposal.updated_at,
    })


@router.delete("/{slug}/proposal/{proposal_id}", status_code=204)
async def delete_proposal(
    slug: str,
    proposal_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = ProposalService(session)
    await service.delete_proposal(proposal_id, user_id=user.id)
    return


@router.get("/{slug}/proposal/{proposal_id}/export")
async def export_proposal(
    slug: str,
    proposal_id: UUID,
    format: str = Query("markdown", description="Format to export (markdown, json)"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = ProposalService(session)
    exported = await service.export_proposal(proposal_id, format=format, user_id=user.id)
    return {"format": format, "data": exported}


# ─── Outreach ─────────────────────────────────────────────────────────────────

@router.get("/{slug}/opportunity/{opportunity_id}/outreach")
async def generate_outreach(
    slug: str,
    opportunity_id: UUID,
    contact_name: Optional[str] = None,
    strategy: str = Query("helpful_observation"),
    channel: str = Query("instagram"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = ProposalService(session)
    outreach = await service.generate_outreach(
        opportunity_id,
        slug,
        contact_name=contact_name or "",
        strategy=strategy,
        channel=channel,
        user_id=user.id
    )
    return {"message": outreach}



# ─── Business CRUD ────────────────────────────────────────────────────────────

@router.post("/", response_model=BusinessCard)
async def create_business(
    payload: BusinessCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    return await service.create_business(payload, user.id)


@router.put("/{slug}", response_model=BusinessCard)
async def update_business(
    slug: str,
    payload: BusinessUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    return await service.update_business(slug, payload, user.id)


@router.delete("/{slug}", status_code=204)
async def delete_business(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessService(session)
    await service.delete_business(slug, user.id)
    return


# ─── Business Contacts ────────────────────────────────────────────────────────

@router.get("/{slug}/contacts", response_model=list[BusinessContactOut])
async def list_contacts(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    b = await biz_service.business_repo.get_by_slug(slug, user.id)
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
    b = await biz_service.business_repo.get_by_slug(slug, user.id)
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
    b = await biz_service.business_repo.get_by_slug(slug, user.id)
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
    b = await biz_service.business_repo.get_by_slug(slug, user.id)
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")

    contact_service = BusinessContactService(session)
    existing = await contact_service.get_contact(contact_id)
    if not existing or existing.business_id != b.id:
        raise HTTPException(status_code=404, detail="Contact not found")

    await contact_service.delete_contact(contact_id)
    return


# ─── Contact Discovery ────────────────────────────────────────────────────────

from app.services.contact_discovery_service import ContactDiscoveryService
from app.schemas.contact_discovery import ContactDiscoveryResponse

@router.post("/{slug}/contact-discovery", response_model=ContactDiscoveryResponse)
async def generate_contact_discovery(
    slug: str,
    force: bool = False,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    business = await biz_service.business_repo.get_by_slug(slug, user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    if business.website:
        raise HTTPException(status_code=400, detail="Contact discovery is only for businesses without a website")
        
    return await ContactDiscoveryService.discover_contacts(session, business, force=force)

@router.get("/{slug}/contact-discovery", response_model=ContactDiscoveryResponse)
async def get_contact_discovery(
    slug: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    business = await biz_service.business_repo.get_by_slug(slug, user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    record = await ContactDiscoveryService.get_latest_discovery(session, business.id)
    if not record:
        raise HTTPException(status_code=404, detail="No contact discovery found")
        
    return record

@router.post("/{slug}/contact-discovery/generate", response_model=ContactDiscoveryResponse)
async def generate_contact_outreach_endpoint(
    slug: str,
    force: bool = False,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    biz_service = BusinessService(session)
    business = await biz_service.business_repo.get_by_slug(slug, user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    if business.website:
        raise HTTPException(status_code=400, detail="Contact discovery outreach is only for businesses without a website")
        
    # Get phone if available
    phone = ""
    contact_service = BusinessContactService(session)
    contacts = await contact_service.get_contacts_for_business(business.id)
    for c in contacts:
        if c.phone:
            phone = c.phone
            break
            
    try:
        return await ContactDiscoveryService.generate_outreach(session, business, phone, force=force)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
