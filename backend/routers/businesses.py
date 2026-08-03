"""Business listing, search, and detail endpoints."""
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from services.auth_service import get_current_user
from services.scoring import compute_opportunity_score, get_recommendation, score_tier

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


class BusinessCard(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    city: str
    country: str
    bio: str
    followers: int
    engagement_rate: float
    website: Optional[str]
    instagram: Optional[str]
    facebook: Optional[str]
    cover_image: str
    opportunity_score: int
    tier: str
    verified: bool


def _to_card(b: dict) -> dict:
    score = compute_opportunity_score(b)
    return {
        "id": b["id"],
        "slug": b["slug"],
        "name": b["name"],
        "category": b["category"],
        "city": b["city"],
        "country": b["country"],
        "bio": b.get("bio", ""),
        "followers": b.get("followers", 0),
        "engagement_rate": b.get("engagement_rate", 0.0),
        "website": b.get("website"),
        "instagram": b.get("instagram"),
        "facebook": b.get("facebook"),
        "cover_image": b.get("cover_image", ""),
        "opportunity_score": score,
        "tier": score_tier(score),
        "verified": b.get("verified", False),
    }


@router.get("")
async def list_businesses(
    request: Request,
    q: Optional[str] = Query(None, description="Free text query"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    website_status: Optional[str] = Query(None, regex="^(has|missing)$"),
    min_followers: Optional[int] = 0,
    min_score: Optional[int] = 0,
    sort: str = Query("score_desc", regex="^(score_desc|followers_desc|name_asc)$"),
    limit: int = Query(60, ge=1, le=200),
    user=Depends(get_current_user),
):
    db = request.state.db
    filters: dict = {}
    if q:
        rx = {"$regex": re.escape(q), "$options": "i"}
        filters["$or"] = [{"name": rx}, {"category": rx}, {"city": rx}, {"country": rx}, {"bio": rx}]
    if category and category != "All":
        filters["category"] = category
    if city:
        filters["city"] = {"$regex": re.escape(city), "$options": "i"}
    if website_status == "has":
        filters["website"] = {"$ne": None}
    elif website_status == "missing":
        filters["website"] = None
    if min_followers:
        filters["followers"] = {"$gte": int(min_followers)}

    cursor = db.businesses.find(filters, {"_id": 0}).limit(limit)
    docs = await cursor.to_list(length=limit)
    cards = [_to_card(d) for d in docs]
    if min_score:
        cards = [c for c in cards if c["opportunity_score"] >= int(min_score)]

    if sort == "score_desc":
        cards.sort(key=lambda x: x["opportunity_score"], reverse=True)
    elif sort == "followers_desc":
        cards.sort(key=lambda x: x["followers"], reverse=True)
    elif sort == "name_asc":
        cards.sort(key=lambda x: x["name"].lower())

    # Save to search history if there was a real query
    if q or category or website_status or min_followers or min_score:
        await db.search_history.insert_one({
            "user_id": user["id"],
            "query": q or "",
            "filters": {
                "category": category,
                "city": city,
                "website_status": website_status,
                "min_followers": min_followers,
                "min_score": min_score,
            },
            "result_count": len(cards),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return {"total": len(cards), "results": cards}


@router.get("/categories")
async def list_categories(request: Request, user=Depends(get_current_user)):
    db = request.state.db
    cats = await db.businesses.distinct("category")
    return {"categories": sorted(cats)}


@router.get("/stats")
async def platform_stats(request: Request, user=Depends(get_current_user)):
    db = request.state.db
    total = await db.businesses.count_documents({})
    missing = await db.businesses.count_documents({"website": None})
    docs = await db.businesses.find({}, {"_id": 0}).to_list(length=500)
    high = sum(1 for d in docs if compute_opportunity_score(d) >= 75)
    avg_score = int(sum(compute_opportunity_score(d) for d in docs) / max(1, len(docs)))
    by_cat: dict = {}
    for d in docs:
        by_cat[d["category"]] = by_cat.get(d["category"], 0) + 1
    top_leads = sorted(docs, key=compute_opportunity_score, reverse=True)[:5]
    return {
        "total_businesses": total,
        "missing_website": missing,
        "high_opportunity": high,
        "avg_score": avg_score,
        "by_category": by_cat,
        "top_leads": [_to_card(d) for d in top_leads],
    }


@router.get("/{slug}")
async def get_business(slug: str, request: Request, user=Depends(get_current_user)):
    db = request.state.db
    b = await db.businesses.find_one({"slug": slug}, {"_id": 0})
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    return {
        "business": _to_card(b),
        "detail": {
            "phone": b.get("phone"),
            "has_online_orders": b.get("has_online_orders", False),
            "posts_last_30": b.get("posts_last_30", 0),
        },
        "recommendation": get_recommendation(b),
    }


@router.get("/{slug}/proposal")
async def get_proposal(slug: str, request: Request, user=Depends(get_current_user)):
    db = request.state.db
    b = await db.businesses.find_one({"slug": slug}, {"_id": 0})
    if not b:
        raise HTTPException(status_code=404, detail="Business not found")
    rec = get_recommendation(b)
    proposal = {
        "prepared_for": b["name"],
        "prepared_by": user.get("name") or user.get("email"),
        "date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "summary": (
            f"{b['name']} has built a strong presence on Instagram with "
            f"{b.get('followers', 0):,} followers, yet lacks a dedicated website "
            f"to convert this audience into direct customers. A tailored "
            f"'{rec['theme']}' web experience will unlock owned traffic, "
            f"bookings, and long-term brand equity."
        ),
        "deliverables": rec["suggested_sections"],
        "timeline_weeks": 4 if rec["price_range"]["max"] < 4000 else 6,
        "price_range": rec["price_range"],
        "theme": rec["theme"],
        "palette": rec["palette"],
        "tier": rec["tier"],
        "score": rec["score"],
        "rationale": rec["rationale"],
    }
    return proposal
