import json
import logging
import hashlib
from duckduckgo_search import DDGS

from app.core.config import get_settings
from app.services.analysis.deterministic_scoring import score_website_candidate
from app.services.analysis.cache import get_candidate_cache, set_candidate_cache
from app.services.analysis.ai_verification import verify_website_candidates
from app.services.analysis.verification_gate import apply_verification_gate

logger = logging.getLogger(__name__)

async def discover_official_website(business_name: str, category: str, city: str, state: str, country: str, address: str = "") -> dict:
    """
    Search DuckDuckGo for the official website of a business and evaluate candidates deterministically.
    Returns structured candidate evidence.
    """
    location_str = f"{city} {state}" if state else city
    
    # Deterministic Identity Hash
    identity_str = f"{business_name.lower()}|{location_str.lower()}"
    business_hash = hashlib.sha256(identity_str.encode()).hexdigest()
    
    cached = await get_candidate_cache("website", business_hash)
    if cached is not None:
        raw_candidates = cached
    else:
        queries = [
            f"{business_name} {location_str} official website",
            f"{business_name} {category} {location_str}"
        ]
        
        raw_candidates = []
        try:
            ddgs = DDGS()
            for query in queries:
                results = ddgs.text(query, max_results=3)
                if results:
                    for r in results:
                        raw_candidates.append({
                            "title": r.get("title", ""),
                            "body": r.get("body", ""),
                            "url": r.get("href", "")
                        })
            
            await set_candidate_cache("website", business_hash, raw_candidates)
        except Exception as e:
            logger.error(f"Website discovery search failed: {e}")
            return {"website": None, "confidence": 0, "status": "NOT_CHECKED", "reasoning": "Search failed", "evidence": []}

    if not raw_candidates:
        return {"website": None, "confidence": 0, "status": "UNVERIFIED", "reasoning": "No search results found", "evidence": []}

    # Deduplicate by URL
    seen_urls = set()
    unique_candidates = []
    for c in raw_candidates:
        url = c.get("url", "").lower()
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_candidates.append(c)

    scored_candidates = []
    for c in unique_candidates:
        score = score_website_candidate(c, business_name, city)
        if score > 0:
            c_copy = c.copy()
            c_copy["score"] = score
            scored_candidates.append(c_copy)
            
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    if not scored_candidates or scored_candidates[0]["score"] < 40:
        return {
            "website": None, 
            "confidence": 0, 
            "status": "UNVERIFIED", 
            "reasoning": "No candidate passed deterministic threshold", 
            "evidence": scored_candidates
        }

    # Phase 2: Call AI Verification
    ai_decision = await verify_website_candidates(business_name, category, city, state, country, scored_candidates)
    
    # Final Rejection Gate
    final_result = apply_verification_gate(ai_decision, scored_candidates, min_deterministic_score=40.0)
    
    return {
        "website": final_result["url"],
        "confidence": final_result["confidence"],
        "status": final_result["status"],
        "reasoning": final_result["reasoning"],
        "evidence": scored_candidates
    }

