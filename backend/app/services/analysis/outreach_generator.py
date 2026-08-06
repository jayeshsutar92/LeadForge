import random
from typing import Any, Dict


def generate_subject_lines(business_name: str, main_pain: str) -> list[str]:
    return [
        f"Quick question regarding {business_name}'s online presence",
        f"Ideas for {business_name} to improve customer acquisition",
        f"Noticed an opportunity for {business_name}",
        f"Helping {business_name} stand out online",
    ]


def generate_ctas() -> list[str]:
    return [
        "Would you be open to a quick 10-minute chat this week to discuss it?",
        "Are you available for a brief call next Tuesday?",
        "If this sounds interesting, let me know and I'll send over a few times to connect.",
        "Reply 'yes' and I'll send over the detailed breakdown.",
    ]


def generate_outreach(business_name: str, opp_data: Dict[str, Any], contact_name: str = "") -> Dict[str, Any]:
    """Deterministically generate outreach email templates based on opportunity insights."""
    
    tier = opp_data.get("tier", "C")
    rationale = opp_data.get("rationale", [])
    
    greeting = f"Hi {contact_name}," if contact_name else "Hi there,"
    
    # Analyze the rationale to personalize the message
    pain_points = []
    if any("No website" in r for r in rationale):
        pain_points.append("I noticed you don't have a dedicated website for your business yet.")
    if any("WordPress" in r or "Wix" in r for r in rationale):
        pain_points.append("I noticed you're currently using a template builder, which might be limiting your site's performance and customization.")
    if any("SEO" in r for r in rationale):
        pain_points.append("I ran a quick audit on your site and noticed some missing SEO tags that might be hurting your search rankings.")
        
    main_pain = pain_points[0] if pain_points else "I was reviewing your online presence and saw some great opportunities for growth."
    
    if tier == "A":
        value_prop = "We specialize in high-performance digital overhauls for businesses like yours. We can help you dramatically increase your conversion rates."
    elif tier == "B":
        value_prop = "We help businesses like yours upgrade their digital presence to stand out from the competition and attract more customers."
    else:
        value_prop = "We build affordable, professional websites that help you get found online easily."

    subjects = generate_subject_lines(business_name, main_pain)
    ctas = generate_ctas()

    # Template 1: Value-Driven (Standard)
    cold_email_value = f"""{greeting}

{main_pain} {value_prop}

I've put together a brief proposal outlining exactly how we can help {business_name} grow, including a breakdown of the strategy and timeline.

{ctas[0]}

Best regards,
[Your Name]"""

    # Template 2: Direct (Aggressive)
    cold_email_direct = f"""{greeting}

Are you currently taking on new clients at {business_name}?

{main_pain} By fixing this, you could capture significantly more traffic. {value_prop}

{ctas[1]}

Best,
[Your Name]"""

    # Template 3: Consultative
    cold_email_consultative = f"""{greeting}

I've been analyzing businesses in your area and {business_name} stood out to me. {main_pain}

We've helped similar businesses solve exactly this problem. I put together a quick breakdown of what a solution looks like.

{ctas[2]}

Thanks,
[Your Name]"""

    # Follow-up Email
    follow_up_email = f"""{greeting}

I know things get busy, so I'm just bubbling this up to the top of your inbox. 

Did you have a chance to review the ideas I sent over for {business_name}? I'd love to show you a quick preview of what we could do for you.

{ctas[3]}

Best,
[Your Name]"""

    return {
        "subject_lines": subjects,
        "call_to_actions": ctas,
        "templates": {
            "value_driven": cold_email_value,
            "direct": cold_email_direct,
            "consultative": cold_email_consultative,
            "follow_up": follow_up_email,
        },
        "personalized_opener": main_pain
    }
