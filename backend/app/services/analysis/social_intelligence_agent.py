import json
import logging
from duckduckgo_search import DDGS

from app.agents.providers.factory import ProviderFactory
from app.core.config import get_settings

logger = logging.getLogger(__name__)

import re
import httpx
import asyncio

async def fetch_profile_metadata(url: str) -> dict:
    metadata = {}
    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as client:
            res = await client.get(url)
            if res.status_code == 200:
                text = res.text
                og_title = re.search(r'<meta\s+(?:property|name)=["\']og:title["\']\s+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
                if og_title: metadata['display_name'] = og_title.group(1)
                else:
                    title = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
                    if title: metadata['display_name'] = title.group(1)
                og_desc = re.search(r'<meta\s+(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
                if og_desc: metadata['bio'] = og_desc.group(1)
                else:
                    meta_desc = re.search(r'<meta\s+(?:property|name)=["\']description["\']\s+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
                    if meta_desc: metadata['bio'] = meta_desc.group(1)
    except Exception:
        pass
    return metadata

async def discover_social_profiles(business_name: str, category: str, city: str, country: str, address: str = "", phone: str = "", website: str = "") -> dict:
    """
    Search DuckDuckGo for public social profiles and use the LLM to filter and extract them.
    Returns a dictionary of profiles, scores, and recommended channel.
    """
    platforms = [
        ("instagram", "site:instagram.com"),
        ("facebook", "site:facebook.com"),
        ("linkedin", "site:linkedin.com"),
        ("x", "site:x.com OR site:twitter.com"),
    ]
    
    # We will gather search snippets for the LLM
    search_results = []
    
    try:
        ddgs = DDGS()
        for platform_name, search_prefix in platforms:
            query = f"{search_prefix} {business_name} {city}"
            # get up to 3 results per platform
            results = ddgs.text(query, max_results=3)
            if results:
                for r in results:
                    search_results.append({
                        "platform": platform_name,
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "href": r.get("href", "")
                    })
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        # Even if search fails partially, we continue with what we have
        pass

    if not search_results:
        return {
            "profiles": [],
            "recommended_platform": None,
            "messages": {}
        }
        
    prompt = f"""
You are an expert Social Intelligence agent. Your task is to identify the official social media profiles for a business based on search results.

Business Context:
- Name: {business_name}
- Category: {category}
- Location: {city}, {country}
- Address/Bio Details: {address}

Search Results:
{json.dumps(search_results, indent=2)}

Task:
1. Review the search results and identify the OFFICIAL profiles for this exact business.
2. If you cannot confidently identify an official profile, you MUST STILL return the BEST candidate profile(s) you found. NEVER return an empty profiles list if you have candidate URLs.
3. For each profile, assign a confidence score (0-100). If it's a candidate but you aren't certain, assign a lower confidence score (e.g., under 80).
4. Determine the 'recommended_platform' for outreach based on which profile seems most active or professional (e.g., if Instagram is 95 confidence and Facebook is 80, recommend Instagram).
5. Generate a short, personalized outreach message for EACH discovered platform. Do NOT mention that you searched for them, just say you came across their profile.

Format your output strictly as a JSON object adhering to this schema. DO NOT include markdown formatting or extra text.
"""

    schema = {
        "type": "object",
        "properties": {
            "profiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["instagram", "facebook", "linkedin", "x"]},
                        "url": {"type": "string"},
                        "username": {"type": "string"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["platform", "url", "username", "confidence", "reasoning"]
                }
            },
            "recommended_platform": {
                "type": ["string", "null"]
            },
            "messages": {
                "type": "object",
                "description": "A dictionary where the key is the platform name, and the value is the generated outreach message."
            }
        },
        "required": ["profiles", "recommended_platform", "messages"]
    }
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider: {e}")
        return {
            "profiles": [],
            "recommended_platform": None,
            "messages": {}
        }
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        
        # Phase 11: Deterministic Profile Verification
        if result and "profiles" in result:
            verified_profiles = []
            highest_score = 0
            best_platform = None
            
            # Fetch metadata concurrently
            async def enrich_profile(p: dict):
                meta = await fetch_profile_metadata(p.get("url", ""))
                p["display_name"] = meta.get("display_name", "")
                p["bio"] = meta.get("bio", "")
                return p
                
            enriched = await asyncio.gather(*(enrich_profile(p) for p in result["profiles"]))
            
            for p in enriched:
                score = 0
                evidence = []
                content = f"{p.get('title','')} {p.get('body','')} {p.get('display_name','')} {p.get('bio','')} {p.get('reasoning','')} {p.get('username', '')}".lower()
                
                # Disqualifiers
                disqualifiers = ["influencer", "blogger", "tourist guide", "visit ", "explore ", "official tourism", "tourism board", "city of", "municipality"]
                if any(dq in content for dq in disqualifiers):
                    p["confidence"] = 0
                    p["evidence"] = ["Disqualified (Tourist/Influencer profile)"]
                    p["status"] = "Rejected"
                    verified_profiles.append(p)
                    continue

                business_name_cleaned = re.sub(r'[^a-z0-9]', '', business_name.lower())
                if p.get("username") and (p["username"].lower() == business_name_cleaned or p["username"].lower() in business_name_cleaned):
                    score += 35
                    evidence.append("Username Match")

                if business_name and business_name.lower() in content:
                    score += 30
                    evidence.append("Name Match")
                elif business_name and any(word.lower() in content for word in business_name.split() if len(word) > 3):
                    score += 15
                    evidence.append("Partial Name Match")
                    
                if p.get("display_name") and business_name.lower() in p.get("display_name").lower():
                    score += 20
                    evidence.append("Display Name Match")
                    
                if city and city.lower() in content:
                    score += 20
                    evidence.append("City Match")
                    
                if country and country.lower() not in ["unknown", ""] and country.lower() in content:
                    score += 10
                    evidence.append("Country Match")
                    
                if category and category.lower() in content:
                    score += 15
                    evidence.append("Category Match")
                    
                if phone and re.sub(r'[^0-9]', '', phone) in re.sub(r'[^0-9]', '', content):
                    score += 25
                    evidence.append("Phone Match")
                    
                if address and address.split(',')[0].lower() in content:
                    score += 20
                    evidence.append("Address Match")
                    
                if website and website.replace("https://", "").replace("http://", "").replace("www.", "").strip("/") in content:
                    score += 25
                    evidence.append("Website Match")
                    
                score = min(score, 100)
                p["confidence"] = score
                p["evidence"] = evidence
                
                if score >= 65:
                    p["status"] = "Verified"
                    if score > highest_score:
                        highest_score = score
                        best_platform = p.get("platform")
                elif score >= 35:
                    p["status"] = "Possible Match"
                else:
                    p["status"] = "Rejected"
                    
                verified_profiles.append(p)
                
            # If no profile satisfies the threshold, return No Verified Profile
            result["profiles"] = verified_profiles
            result["recommended_platform"] = best_platform
            
        return result
    except Exception as e:
        logger.error(f"Failed to generate social intelligence from LLM: {e}")
        return {
            "profiles": [],
            "recommended_platform": None,
            "messages": {}
        }
