from typing import Any, Dict
import json
from app.core.config import get_settings
from app.agents.providers.factory import ProviderFactory
import logging

logger = logging.getLogger(__name__)

async def generate_outreach(business_name: str, opp_data: Dict[str, Any], contact_name: str = "") -> Dict[str, Any]:
    """Use AI to generate personalized outreach email templates."""
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider for outreach: {e}")
        raise ValueError(f"AI Provider error: {e}")

    schema = {
        "type": "object",
        "properties": {
            "subject_lines": {
                "type": "array",
                "items": {"type": "string"},
                "description": "4 variations of subject lines."
            },
            "call_to_actions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "4 variations of call to actions."
            },
            "templates": {
                "type": "object",
                "properties": {
                    "value_driven": {"type": "string"},
                    "direct": {"type": "string"},
                    "consultative": {"type": "string"},
                    "follow_up": {"type": "string"}
                },
                "required": ["value_driven", "direct", "consultative", "follow_up"]
            },
            "personalized_opener": {"type": "string", "description": "The main pain point identified as an opener."}
        },
        "required": ["subject_lines", "call_to_actions", "templates", "personalized_opener"]
    }
    
    greeting = f"Hi {contact_name}," if contact_name else "Hi there,"
    
    prompt = f"""
    You are an expert B2B sales copywriter. Generate personalized outreach email templates for {business_name}.
    Greeting to use: {greeting}
    
    Opportunity Data:
    {json.dumps(opp_data, indent=2)}
    
    Generate 4 subject lines, 4 call to actions, and 4 email templates (value_driven, direct, consultative, follow_up).
    Make them highly specific to the insights in the Opportunity Data (e.g. mention if they lack a website, or have poor SEO).
    """
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        return result
    except Exception as e:
        logger.error(f"AI generation failed for outreach: {e}")
        raise ValueError(f"AI generation failed: {e}")
