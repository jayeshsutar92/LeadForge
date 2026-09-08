import json
import logging
import hashlib
from duckduckgo_search import DDGS

from app.core.config import get_settings
from app.services.analysis.deterministic_scoring import score_website_candidate
from app.services.analysis.cache import get_candidate_cache, set_candidate_cache

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

    # Return top structured evidence, but DO NOT declare VERIFIED
    # We are pausing AI verification for Phase 1. Return the best UNVERIFIED candidate.
    best_candidate = scored_candidates[0]
    return {
        "website": best_candidate["url"],
        "confidence": best_candidate["score"],
        "status": "UNVERIFIED", # Explicitly unverified until Phase 2 AI
        "reasoning": "Deterministic scoring complete, pending AI verification",
        "evidence": scored_candidates
    }

