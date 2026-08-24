from typing import Any, Dict
import json
from app.core.config import get_settings
from app.agents.providers.factory import ProviderFactory
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def generate_opportunity(bi_data: Dict[str, Any], business_name: str) -> Dict[str, Any]:
    """Use AI to analyze BI data and generate a structured opportunity."""
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider: {e}")
        raise HTTPException(status_code=502, detail=f"AI Provider error: {e}")

    schema = {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "description": "Score from 0 to 100 based on website needs and opportunity."},
            "tier": {"type": "string", "enum": ["A", "B", "C"], "description": "Opportunity tier."},
            "rationale": {
                "type": "array", 
                "items": {"type": "string"},
                "description": "List of reasons for the score."
            },
            "recommendations": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "palette": {"type": "array", "items": {"type": "string"}},
                    "suggested_sections": {"type": "array", "items": {"type": "string"}},
                    "price_range": {"type": "string"},
                    "estimated_timeline": {"type": "string"}
                },
                "required": ["theme", "palette", "suggested_sections", "price_range", "estimated_timeline"]
            }
        },
        "required": ["score", "tier", "rationale", "recommendations"]
    }
    
    prompt = f"""
    Analyze the following business intelligence data for {business_name} and generate a structured opportunity score, tier, rationale, and design recommendations.
    
    Business Intelligence Data:
    {json.dumps(bi_data, indent=2)}
    
    The score should be between 0 and 100. High score if they have no website or a poor website, low score if they have a great modern website.
    """
    
    import asyncio
    max_retries = 3
    base_delay = 2
    for attempt in range(max_retries):
        try:
            result = await provider.generate_json(prompt=prompt, schema=schema)
            return result
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {base_delay * (2 ** attempt)}s...")
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    raise HTTPException(status_code=429, detail="Generation in progress, please wait.")
            logger.error(f"AI generation failed for opportunity scoring: {e}")
            raise HTTPException(status_code=502, detail=f"AI generation failed: {e}")
