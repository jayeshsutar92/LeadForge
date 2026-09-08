import json
import logging
import hashlib
import asyncio

from app.core.config import get_settings
from app.agents.providers.factory import ProviderFactory
from app.services.analysis.cache import get_ai_decision, set_ai_decision
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

async def verify_website_candidates(business_name: str, category: str, city: str, state: str, country: str, candidates: list[dict]) -> dict:
    """
    Pass the deterministic short list of website candidates to the AI for adjudication.
    Returns: {"decision": "<url> or NONE", "confidence": int, "justification": str}
    """
    if not candidates:
        return {"decision": "NONE", "confidence": 0, "justification": "No deterministic candidates available."}
        
    # Top 3 only to save tokens
    shortlist = candidates[:3]
    
    evidence_payload = {
        "business": {
            "name": business_name,
            "category": category,
            "location": f"{city}, {state}, {country}"
        },
        "candidates": shortlist
    }
    
    evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()
    
    cached = await get_ai_decision(evidence_hash)
    if cached:
        logger.info(f"AI Verification cache hit for {business_name} (website)")
        return cached

    prompt = f"""You are an expert Data Researcher verifying the official website for a business based purely on pre-scored evidence.

Business Context:
{json.dumps(evidence_payload['business'], indent=2)}

Candidate Evidence (Top Pre-scored Results):
{json.dumps(shortlist, indent=2)}

Task:
1. Review the candidate evidence provided.
2. Select the EXACT official website URL from the candidate list if there is strong evidence.
3. If the evidence is ambiguous, conflicting, or insufficient to prove one of the URLs is the official site, return "NONE".
4. DO NOT guess. DO NOT hallucinate URLs that are not in the candidate list.
5. Provide a short, concise justification based ONLY on the evidence.
"""

    schema = {
        "type": "object",
        "properties": {
            "decision": {"type": "string", "description": "The exact URL of the selected official website, or 'NONE' if insufficient evidence."},
            "confidence": {"type": "integer", "description": "Confidence score from 0 to 100."},
            "justification": {"type": "string", "description": "Brief explanation for the decision based on evidence."}
        },
        "required": ["decision", "confidence", "justification"]
    }
    
    settings = get_settings()
    provider = ProviderFactory.get_provider(settings.ai_provider, settings.model_dump())
    
    redis = get_redis_client()
    lock_key = f"lock:ai_decision:{evidence_hash}"
    
    # Try locking to prevent race conditions
    try:
        async with redis.lock(lock_key, timeout=30, blocking_timeout=5):
            # Double check cache inside lock
            cached = await get_ai_decision(evidence_hash)
            if cached:
                return cached
                
            logger.info(f"Calling AI for website verification for {business_name}")
            decision = await provider.generate_json(prompt, schema=schema)
            
            # Basic validation
            if not isinstance(decision, dict) or "decision" not in decision:
                logger.error(f"Malformed AI response for website: {decision}")
                return {"decision": "NONE", "confidence": 0, "justification": "Malformed AI response"}
                
            await set_ai_decision(evidence_hash, decision)
            return decision
    except Exception as e:
        logger.error(f"AI verification failure (timeout/rate-limit) for {business_name}: {e}")
        # Return a special failure object that is not a valid verification
        return {"decision": "FAILED", "confidence": 0, "justification": str(e)}

async def verify_social_candidates(business_name: str, category: str, city: str, state: str, country: str, platforms_candidates: dict) -> dict:
    """
    Pass batched social short lists to the AI.
    platforms_candidates is {"instagram": [...], "facebook": [...]}
    Returns: {"instagram": {"decision": "url or NONE", ...}, "facebook": ...}
    """
    shortlists = {}
    has_candidates = False
    for plat, candidates in platforms_candidates.items():
        if candidates:
            shortlists[plat] = candidates[:3]
            has_candidates = True
        else:
            shortlists[plat] = []
            
    if not has_candidates:
        return {p: {"decision": "NONE", "confidence": 0, "justification": "No candidates"} for p in platforms_candidates}

    evidence_payload = {
        "business": {
            "name": business_name,
            "category": category,
            "location": f"{city}, {state}, {country}"
        },
        "platform_candidates": shortlists
    }
    
    evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()
    
    cached = await get_ai_decision(evidence_hash)
    if cached:
        logger.info(f"AI Verification cache hit for {business_name} (social batched)")
        return cached

    prompt = f"""You are an expert Data Researcher verifying official social media profiles based purely on pre-scored evidence.

Business Context:
{json.dumps(evidence_payload['business'], indent=2)}

Platform Candidate Evidence:
{json.dumps(shortlists, indent=2)}

Task:
1. Review the candidate evidence provided for each platform.
2. For each platform, select the EXACT profile URL from its candidate list if there is strong evidence.
3. If the evidence is ambiguous, conflicting, or insufficient, return "NONE" for that platform.
4. DO NOT guess. DO NOT hallucinate URLs that are not in the list. Keep decisions independent.
5. Provide a short justification for each decision.
"""
    
    # We build a schema for the specific platforms requested
    properties = {}
    for plat in platforms_candidates.keys():
        properties[plat] = {
            "type": "object",
            "properties": {
                "decision": {"type": "string", "description": f"Exact {plat} URL or 'NONE'."},
                "confidence": {"type": "integer", "description": "0 to 100"},
                "justification": {"type": "string", "description": "Brief reason."}
            },
            "required": ["decision", "confidence", "justification"]
        }
        
    schema = {
        "type": "object",
        "properties": properties,
        "required": list(platforms_candidates.keys())
    }
    
    settings = get_settings()
    provider = ProviderFactory.get_provider(settings.ai_provider, settings.model_dump())
    
    redis = get_redis_client()
    lock_key = f"lock:ai_decision_social:{evidence_hash}"
    
    try:
        async with redis.lock(lock_key, timeout=60, blocking_timeout=5):
            cached = await get_ai_decision(evidence_hash)
            if cached:
                return cached
                
            logger.info(f"Calling AI for social verification batched for {business_name}")
            decision = await provider.generate_json(prompt, schema=schema)
            
            if not isinstance(decision, dict):
                logger.error(f"Malformed batched AI response: {decision}")
                return {p: {"decision": "FAILED", "confidence": 0, "justification": "Malformed response"} for p in platforms_candidates}
                
            await set_ai_decision(evidence_hash, decision)
            return decision
    except Exception as e:
        logger.error(f"AI social verification failure for {business_name}: {e}")
        return {p: {"decision": "FAILED", "confidence": 0, "justification": str(e)} for p in platforms_candidates}
