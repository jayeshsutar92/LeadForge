from typing import Any, Dict


def generate_outreach(business_name: str, opp_data: Dict[str, Any], contact_name: str = "") -> Dict[str, str]:
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

    # Cold Email
    cold_email = f"""{greeting}

{main_pain} {value_prop}

I've put together a brief proposal outlining exactly how we can help {business_name} grow, including a breakdown of the strategy and timeline.

Would you be open to a quick 10-minute chat this week to discuss it?

Best regards,
[Your Name]"""

    # Follow-up Email
    follow_up_email = f"""{greeting}

I know things get busy, so I'm just bubbling this up to the top of your inbox. 

Did you have a chance to review the ideas I sent over for {business_name}? I'd love to show you a quick preview of what we could do for you.

Let me know if you have 5 minutes to connect.

Best,
[Your Name]"""

    return {
        "cold_email": cold_email,
        "follow_up_email": follow_up_email,
        "personalized_opener": main_pain
    }
