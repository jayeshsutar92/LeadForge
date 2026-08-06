from typing import Any, Dict


def generate_opportunity(bi_data: Dict[str, Any], business_name: str) -> Dict[str, Any]:
    """Deterministically analyze BI data and generate a structured opportunity."""
    
    # 1. Scoring Logic
    base_score = 50
    tier = "C"
    rationale = []
    
    metadata = bi_data.get("website_metadata", {})
    tech = bi_data.get("technologies", [])
    seo = bi_data.get("seo", {})
    contacts = bi_data.get("contacts", [])
    
    # Check if they have a website based on metadata title
    has_website = bool(metadata.get("title"))
    
    if not has_website:
        base_score += 30
        rationale.append("No website detected: High priority for full digital presence package.")
    else:
        # Tech stack penalization / reward
        if "WordPress" in tech or "Wix" in tech or "Squarespace" in tech:
            base_score += 15
            rationale.append("Uses template builders (WordPress/Wix): Ripe for a custom Next.js/React upgrade.")
        elif "React" in tech or "Next.js" in tech:
            base_score -= 10
            rationale.append("Already using modern frontend technologies (React/Next.js): Harder to upsell.")
            
        # SEO penalization
        if seo.get("has_title") is False or seo.get("has_meta_description") is False:
            base_score += 10
            rationale.append("Missing basic SEO tags (Title/Description): Needs technical SEO overhaul.")
            
        if seo.get("images_without_alt", 0) > 5:
            base_score += 5
            rationale.append("Many images missing ALT text: Accessibility and SEO improvements needed.")
            
    # Contacts reward
    if len(contacts) > 0:
        base_score += 10
        rationale.append(f"Found {len(contacts)} direct contact points: Easier to reach out.")
    else:
        rationale.append("No direct contacts found: May require LinkedIn/Social outreach.")
        
    # Cap score
    score = min(max(base_score, 0), 100)
    
    # Assign Tier
    if score >= 80: tier = "A"
    elif score >= 60: tier = "B"
    else: tier = "C"

    # 2. Recommendations
    if not has_website:
        theme = "Modern, Trust-Building, Corporate"
        sections = ["Home", "About Us", "Services", "Testimonials", "Contact"]
        price = "$3,500 - $6,000"
        timeline = "4 - 6 Weeks"
    else:
        theme = "Performance-Optimized, High-Conversion, Dynamic"
        sections = ["Redesigned Landing", "Service Deep-Dives", "Interactive Portfolio", "Optimized Contact Flow"]
        price = "$5,000 - $8,500"
        timeline = "6 - 8 Weeks"

    return {
        "score": score,
        "tier": tier,
        "rationale": rationale,
        "recommendations": {
            "theme": theme,
            "palette": ["#0f172a", "#3b82f6", "#f8fafc"],  # Slate, Blue, White
            "suggested_sections": sections,
            "price_range": price,
            "estimated_timeline": timeline
        }
    }
