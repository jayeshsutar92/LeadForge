import json
import logging
import hashlib
import re
from duckduckgo_search import DDGS

from app.services.analysis.deterministic_scoring import score_social_candidate
from app.services.analysis.cache import get_candidate_cache, set_candidate_cache
from app.services.analysis.ai_verification import verify_social_candidates
from app.services.analysis.verification_gate import apply_verification_gate

logger = logging.getLogger(__name__)

async def discover_social_profiles(business_name: str, category: str, city: str, state: str, country: str, address: str = "", phone: str = "", website: str = "") -> dict:
    location_str = f"{city} {state}" if state else city
    
    identity_str = f"{business_name.lower()}|{location_str.lower()}"
    business_hash = hashlib.sha256(identity_str.encode()).hexdigest()
    
    platforms = [
        ("instagram", "site:instagram.com"),
        ("facebook", "site:facebook.com"),
        ("linkedin", "site:linkedin.com"),
        ("x", "site:x.com OR site:twitter.com")
    ]
    
    base_slug = re.sub(r'[^a-zA-Z0-9]', '', business_name.lower())
    slug_variants = [
        base_slug,
        f"{base_slug}{city.lower().replace(' ', '')}",
        business_name.lower().replace(' ', '_')
    ]
    
    results_by_platform = {}
    old_profiles_compat = []
    
    try:
        ddgs = DDGS()
        for plat_name, plat_query in platforms:
            cached = await get_candidate_cache(plat_name, business_hash)
            if cached is not None:
                raw_candidates = cached
            else:
                raw_candidates = []
                queries = [
                    f"{plat_query} \"{business_name}\" {location_str}"
                ]
                for slug in set(slug_variants):
                    queries.append(f"{plat_query} {slug}")
                    
                for query in queries:
                    res = ddgs.text(query, max_results=3)
                    if res:
                        for r in res:
                            raw_candidates.append({
                                "title": r.get("title", ""),
                                "body": r.get("body", ""),
                                "url": r.get("href", "")
                            })
                
                await set_candidate_cache(plat_name, business_hash, raw_candidates)
                
            seen_urls = set()
            unique_candidates = []
            for c in raw_candidates:
                url = c.get("url", "").lower()
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_candidates.append(c)

            scored_candidates = []
            for c in unique_candidates:
                score = score_social_candidate(c, business_name, city, plat_name)
                if score > 0:
                    c_copy = c.copy()
                    c_copy["score"] = score
                    scored_candidates.append(c_copy)
                    
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # Phase 2: just collect the scored candidates per platform
            results_by_platform[plat_name] = scored_candidates
                
    except Exception as e:
        logger.error(f"Social discovery search failed (DDG/network): {e}")
        # Failure means we stop generation for everything, and force NOT_CHECKED
        return {
            "profiles": [],
            "recommended_platform": None,
            "messages": [],
            "evidence_pipeline": {
                p[0]: {
                    "url": None,
                    "confidence": 0,
                    "status": "NOT_CHECKED",
                    "reasoning": f"DuckDuckGo search failed: {e}",
                    "evidence": []
                } for p in platforms
            }
        }
            
    # Phase 2: Batched AI Verification
    ai_decisions = await verify_social_candidates(business_name, category, city, state, country, results_by_platform)
    
    final_results = {}
    for plat_name, scored_candidates in results_by_platform.items():
        decision_payload = ai_decisions.get(plat_name, {"decision": "FAILED", "confidence": 0, "justification": "Platform missing from AI response"})
        final_result = apply_verification_gate(decision_payload, scored_candidates, min_deterministic_score=40.0)
        
        final_results[plat_name] = {
            "url": final_result["url"],
            "confidence": final_result["confidence"],
            "status": final_result["status"],
            "reasoning": final_result["reasoning"],
            "evidence": scored_candidates
        }
        
        if final_result["status"] == "VERIFIED":
            old_profiles_compat.append({
                "platform": plat_name,
                "url": final_result["url"],
                "status": "Verified"
            })

    return {
        "profiles": old_profiles_compat,
        "recommended_platform": old_profiles_compat[0]["platform"] if old_profiles_compat else None,
        "messages": [],
        "evidence_pipeline": final_results
    }
