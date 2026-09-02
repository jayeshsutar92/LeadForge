import json
import logging

from app.agents.providers.factory import ProviderFactory
from app.core.config import get_settings

logger = logging.getLogger(__name__)

async def validate_business_category(business_name: str, requested_category: str, osm_type: str = "") -> dict:
    """
    Use the LLM to validate if the discovered business name and OSM type match the requested category.
    Returns a dictionary containing 'is_valid' (bool), and 'reasoning' (str).
    """
    prompt = f"""You are an expert Business Analyst. Your task is to validate whether a discovered business matches the requested category.

Context:
- Discovered Business Name: {business_name}
- OpenStreetMap Place Type/Tags: {osm_type}
- Requested Search Category: {requested_category}

Task:
1. Determine if this business genuinely belongs to the requested category.
2. Reject businesses that are clearly unrelated (e.g., if the category is "Dental practices" but the business is "Smith's Plumbing").
3. Be moderately lenient if the name implies a related service or if it's a generic corporate name that could encompass the category.
4. Output your decision as a boolean 'is_valid' and provide a brief 'reasoning'.

Format your output strictly as a JSON object adhering to this schema. DO NOT include markdown formatting or extra text.
"""

    schema = {
        "type": "object",
        "properties": {
            "is_valid": {
                "type": "boolean",
                "description": "True if the business matches the requested category, False otherwise."
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation for the decision."
            }
        },
        "required": ["is_valid", "reasoning"]
    }
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider for category validation: {e}")
        return {"is_valid": True, "reasoning": "Provider setup failed, defaulting to valid"}
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        return result
    except Exception as e:
        logger.error(f"Category validation AI failed: {e}")
        return {"is_valid": True, "reasoning": "AI validation failed, defaulting to valid"}
