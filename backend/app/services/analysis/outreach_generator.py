from typing import Any, Dict
import json
from app.core.config import get_settings
from app.agents.providers.factory import ProviderFactory
from app.services.analysis.outreach_templates import OUTREACH_TEMPLATES
import logging

logger = logging.getLogger(__name__)

async def generate_outreach(
    business_name: str, 
    opp_data: Dict[str, Any], 
    contact_name: str = "", 
    strategy: str = "helpful_observation", 
    channel: str = "instagram"
) -> str:
    """Use AI to personalize a specific outreach template."""
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider for outreach: {e}")
        raise ValueError(f"AI Provider error: {e}")

    # Fallback to default if not found
    if strategy not in OUTREACH_TEMPLATES:
        strategy = "helpful_observation"
    if channel not in OUTREACH_TEMPLATES[strategy]:
        channel = "instagram"
        
    base_template = OUTREACH_TEMPLATES[strategy][channel]

    schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The finalized personalized message with placeholders filled out naturally."
            }
        },
        "required": ["message"]
    }
    
    contact = contact_name if contact_name else "[Name]"
    
    prompt = f"""
    You are an expert B2B sales copywriter. Your task is to personalize the following outreach template for {business_name}.
    
    Base Template:
    "{base_template}"
    
    Opportunity Data:
    {json.dumps(opp_data, indent=2)}
    
    Instructions:
    1. Fill in the placeholders (e.g., [Business], [Name], [specific detail], [specific product/service], [location/niche]) using the Opportunity Data.
    2. The Contact Name is "{contact}". If it's "[Name]", replace it with a natural greeting or remove the name if appropriate.
    3. If the website has specific issues (e.g., slow, not mobile-friendly, missing), adjust the wording naturally to reflect that, while keeping the tone exactly as the template.
    4. If a specific detail (like a niche or specific product) is missing from the data, generate a natural wording that fits the business context rather than leaving brackets or exposing raw placeholders.
    5. KEEP the message concise and conversational exactly as defined in the template. Do not unnecessarily rewrite the template beyond filling the placeholders and naturalizing the sentences.
    """
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        return result.get("message", base_template)
    except Exception as e:
        logger.error(f"AI generation failed for outreach: {e}")
        raise ValueError(f"AI generation failed: {e}")
