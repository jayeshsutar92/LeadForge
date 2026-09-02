import json
import logging
from duckduckgo_search import DDGS

from app.agents.providers.factory import ProviderFactory
from app.core.config import get_settings

logger = logging.getLogger(__name__)

async def discover_official_website(business_name: str, category: str, city: str, state: str, country: str, address: str = "") -> dict:
    """
    Search DuckDuckGo for the official website of a business and use the LLM to verify it.
    Returns a dictionary containing 'website' (str or None), 'confidence' (int), and 'reasoning' (str).
    """
    location_str = f"{city} {state}" if state else city
    query = f"{business_name} {category} {location_str} official website"
    
    search_results = []
    
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=5)
        if results:
            for r in results:
                search_results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href", "")
                })
    except Exception as e:
        logger.error(f"Website discovery search failed: {e}")
        return {"website": None, "confidence": 0, "reasoning": "Search failed"}

    if not search_results:
        return {"website": None, "confidence": 0, "reasoning": "No search results found"}

    prompt = f"""You are an expert Data Researcher. Your task is to find the official website for a business based on search results.

Business Context:
- Name: {business_name}
- Category: {category}
- Location: {city}{f', {state}' if state else ''}, {country}
- Address Details: {address}

Search Results:
{json.dumps(search_results, indent=2)}

Task:
1. Review the search results and identify the OFFICIAL website for this exact business.
2. Reject directories (e.g., Yelp, YellowPages, TripAdvisor), social media profiles (Facebook, Instagram, LinkedIn), and aggregator sites. Only return the business's own domain.
3. Validate that the website belongs to the business in the specified location, not a different business with a similar name in another location.
4. If you find a verified official website, return its URL. Otherwise, return null.
5. Assign a confidence score (0-100) to your decision.
6. Provide a brief reasoning for your conclusion.

Format your output strictly as a JSON object adhering to this schema. DO NOT include markdown formatting or extra text.
"""

    schema = {
        "type": "object",
        "properties": {
            "website": {
                "type": ["string", "null"],
                "description": "The official website URL if found, or null if no valid official website exists."
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score from 0 to 100."
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation for why this website was chosen or rejected."
            }
        },
        "required": ["website", "confidence", "reasoning"]
    }
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider for website discovery: {e}")
        return {"website": None, "confidence": 0, "reasoning": "Provider setup failed"}
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        return result
    except Exception as e:
        logger.error(f"Website verification AI failed: {e}")
        return {"website": None, "confidence": 0, "reasoning": "AI verification failed"}
