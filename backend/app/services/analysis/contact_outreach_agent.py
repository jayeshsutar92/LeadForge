import json
import logging

from app.agents.providers.factory import ProviderFactory
from app.core.config import get_settings

logger = logging.getLogger(__name__)

async def generate_contact_outreach(
    business_name: str,
    category: str,
    city: str,
    phone: str,
    verified_platforms: list[dict]
) -> dict:
    """
    Generate tailored outreach messages for verified contact discovery platforms.
    """
    if not verified_platforms:
        return {"messages": {}}

    prompt = f"""
You are an expert SDR (Sales Development Representative). Your task is to write personalized outreach messages for a business.
This business DOES NOT have a website, so our primary hook should be offering to help them build a digital presence or website.

Business Context:
- Name: {business_name}
- Category: {category}
- Location: {city}
- Phone: {phone}
- Verified Platforms: {json.dumps(verified_platforms, indent=2)}

Task:
1. For EACH verified platform in the list, write a short, highly personalized outreach message.
2. If phone is provided and valid, also generate a 'whatsapp' message.
3. The message should naturally mention that you noticed they don't have a website (or could use a better digital presence).
4. Match the communication style of the specific platform (e.g., LinkedIn is professional, Instagram is casual, WhatsApp is direct).
5. DO NOT be spammy, pushy, or exaggerated. Keep it concise, friendly, and focused on value.

Format your output strictly as a JSON object adhering to this schema.
"""

    schema = {
        "type": "object",
        "properties": {
            "messages": {
                "type": "object",
                "description": "A dictionary where the key is the platform name (e.g., instagram, facebook, linkedin, x, whatsapp), and the value is the generated outreach message."
            }
        },
        "required": ["messages"]
    }
    
    settings = get_settings()
    config = settings.model_dump()
    
    try:
        provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
    except Exception as e:
        logger.error(f"Failed to load AI provider: {e}")
        return {"messages": {}}
    
    try:
        result = await provider.generate_json(prompt=prompt, schema=schema)
        return result
    except Exception as e:
        logger.error(f"Failed to generate contact outreach from LLM: {e}")
        return {"messages": {}}
