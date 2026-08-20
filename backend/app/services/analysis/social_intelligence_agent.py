import json
import logging
from duckduckgo_search import DDGS

from app.agents.providers.factory import ProviderFactory
from app.core.config import get_settings

logger = logging.getLogger(__name__)

async def discover_social_profiles(business_name: str, category: str, city: str, country: str) -> dict:
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

Search Results:
{json.dumps(search_results, indent=2)}

Task:
1. Review the search results and identify the OFFICIAL profiles for this exact business. Be careful not to select profiles of similarly named businesses in other cities.
2. For each verified profile, assign a confidence score (0-100).
3. Determine the 'recommended_platform' for outreach based on which profile seems most active or professional (e.g., if Instagram is 95 confidence and Facebook is 80, recommend Instagram).
4. Generate a short, personalized outreach message for EACH discovered platform. Do NOT mention that you searched for them, just say you came across their profile.

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
    provider = ProviderFactory.create(settings.AI_MODEL)
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        return result
    except Exception as e:
        logger.error(f"Failed to generate social intelligence from LLM: {e}")
        return {
            "profiles": [],
            "recommended_platform": None,
            "messages": {}
        }
