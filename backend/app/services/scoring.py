"""Rule-based Opportunity Score + website recommendation engine.

Score range: 0-100. Higher = more likely to benefit from a website.
"""
from typing import Dict, List, Any


CATEGORY_THEMES: Dict[str, Dict[str, Any]] = {
    "Restaurant": {
        "theme": "Warm Appetite",
        "palette": ["#2B1810", "#E8B04C", "#F5EDE0"],
        "sections": ["Hero with signature dish", "Menu", "Reservations", "Location & Hours", "Gallery", "Reviews"],
        "budget": (1500, 3500),
    },
    "Fashion": {
        "theme": "Editorial Minimal",
        "palette": ["#0A0A0A", "#F2F2F2", "#D6A55A"],
        "sections": ["Hero lookbook", "Collections", "Product Grid", "About the Brand", "Lookbook", "Contact"],
        "budget": (3500, 8000),
    },
    "Beauty": {
        "theme": "Soft Editorial",
        "palette": ["#F8E6E6", "#3B2E2A", "#C48B7A"],
        "sections": ["Hero", "Services", "Booking", "Before/After Gallery", "Team", "Reviews"],
        "budget": (1500, 3500),
    },
    "Fitness": {
        "theme": "Bold Kinetic",
        "palette": ["#0F0F0F", "#22C55E", "#FFFFFF"],
        "sections": ["Hero video", "Programs", "Trainers", "Class Schedule", "Pricing", "Contact"],
        "budget": (2000, 4500),
    },
    "Cafe": {
        "theme": "Cozy Craft",
        "palette": ["#3E2C1F", "#E8DCC4", "#B77A3C"],
        "sections": ["Hero", "Menu", "Story", "Location", "Instagram Feed"],
        "budget": (1000, 2500),
    },
    "Photography": {
        "theme": "Gallery Minimal",
        "palette": ["#111111", "#FAFAFA", "#8A8A8A"],
        "sections": ["Fullscreen Portfolio", "About", "Services", "Pricing", "Contact"],
        "budget": (2000, 5000),
    },
    "Handmade": {
        "theme": "Craft Warm",
        "palette": ["#5B3A1E", "#E8D8B6", "#A66A2C"],
        "sections": ["Hero", "Shop", "Story", "Process", "Contact"],
        "budget": (1500, 3500),
    },
    "Wellness": {
        "theme": "Calm Botanical",
        "palette": ["#2F4A3A", "#F0EBE1", "#B4A28A"],
        "sections": ["Hero", "Services", "Booking", "Practitioners", "Blog", "Contact"],
        "budget": (1500, 4000),
    },
    "Tech": {
        "theme": "Modern Signal",
        "palette": ["#0B1220", "#00E5FF", "#F5F7FA"],
        "sections": ["Hero", "Features", "How it Works", "Pricing", "Case Studies", "Contact"],
        "budget": (3000, 7500),
    },
    "Food": {
        "theme": "Fresh Market",
        "palette": ["#1F3D2B", "#F6E9C8", "#D18B47"],
        "sections": ["Hero", "Products", "Order Online", "Story", "Locations"],
        "budget": (1500, 3500),
    },
}

DEFAULT_THEME = {
    "theme": "Modern Clean",
    "palette": ["#0F172A", "#22D3EE", "#F8FAFC"],
    "sections": ["Hero", "About", "Services", "Gallery", "Contact"],
    "budget": (1500, 3500),
}


def compute_opportunity_score(biz: dict) -> int:
    score = 0
    has_website = bool(biz.get("website"))
    if not has_website:
        score += 45
    followers = int(biz.get("followers", 0))
    engagement = float(biz.get("engagement_rate", 0.0))
    posts_last_30 = int(biz.get("posts_last_30", 0))

    if followers >= 50000:
        score += 20
    elif followers >= 10000:
        score += 15
    elif followers >= 3000:
        score += 8
    else:
        score += 3

    if engagement >= 4.0:
        score += 12
    elif engagement >= 2.0:
        score += 8
    elif engagement >= 1.0:
        score += 4

    if posts_last_30 >= 15:
        score += 10
    elif posts_last_30 >= 5:
        score += 6

    if biz.get("has_online_orders") is False and biz.get("category") in ("Restaurant", "Cafe", "Handmade", "Fashion", "Food"):
        score += 8

    return max(0, min(100, score))


def score_tier(score: int) -> str:
    if score >= 75:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    return "LOW"


def get_recommendation(biz: dict) -> dict:
    tpl = CATEGORY_THEMES.get(biz.get("category", ""), DEFAULT_THEME)
    score = compute_opportunity_score(biz)
    lo, hi = tpl["budget"]
    if score >= 75:
        lo = int(lo * 1.1)
        hi = int(hi * 1.25)
    tier = score_tier(score)

    rationale: List[str] = []
    if not biz.get("website"):
        rationale.append("No website detected — high conversion loss from social to bookings.")
    if biz.get("followers", 0) >= 10000:
        rationale.append(f"Strong social audience of {biz['followers']:,} followers — ready for owned traffic.")
    if biz.get("engagement_rate", 0) >= 3.0:
        rationale.append("Above-average engagement — audience is warm and would visit a site.")
    if biz.get("category") in ("Restaurant", "Cafe") and not biz.get("has_online_orders"):
        rationale.append("Missing online ordering — direct revenue channel opportunity.")
    if not rationale:
        rationale.append("Existing digital footprint can be upgraded to convert social traffic more efficiently.")

    return {
        "score": score,
        "tier": tier,
        "theme": tpl["theme"],
        "palette": tpl["palette"],
        "suggested_sections": tpl["sections"],
        "price_range": {"min": lo, "max": hi, "currency": "USD"},
        "rationale": rationale,
    }
