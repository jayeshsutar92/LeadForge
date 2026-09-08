import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Very basic blocklist
BLOCKLIST_DOMAINS = {
    "facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com",
    "yelp.com", "yellowpages.com", "tripadvisor.com", "foursquare.com",
    "mapquest.com", "google.com", "yahoo.com", "bing.com"
}

def string_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100.0

def score_website_candidate(candidate: dict, business_name: str, city: str) -> float:
    url = candidate.get("url", "").lower()
    title = candidate.get("title", "")
    body = candidate.get("body", "")
    
    # 1. Blocklist check
    if any(domain in url for domain in BLOCKLIST_DOMAINS):
        return 0.0
        
    score = 0.0
    
    # 2. Name match (title or url)
    title_match = string_similarity(business_name, title)
    
    # Extract domain logic simplified
    domain = url.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
    domain_match = string_similarity(business_name.replace(" ", ""), domain.split(".")[0])
    
    score += max(title_match, domain_match) * 0.6  # 60% weight
    
    # 3. Location match
    if city and city.lower() in (title + " " + body).lower():
        score += 30.0  # 30% weight
        
    # 4. Structural hints
    if "contact" in url or "about" in url or "official" in title.lower():
        score += 10.0
        
    return min(score, 100.0)

def score_social_candidate(candidate: dict, business_name: str, city: str, platform: str) -> float:
    url = candidate.get("url", "").lower()
    title = candidate.get("title", "")
    body = candidate.get("body", "")
    
    score = 0.0
    
    # Check if url actually belongs to the platform
    if platform not in url:
        return 0.0
        
    # Extract username/slug roughly
    parts = [p for p in url.split("/") if p]
    username = parts[-1] if parts else ""
    
    # 1. Username similarity
    username_match = string_similarity(business_name.replace(" ", ""), username)
    title_match = string_similarity(business_name, title)
    score += max(username_match, title_match) * 0.6
    
    # 2. Bio/Location match
    if city and city.lower() in (title + " " + body).lower():
        score += 40.0
        
    return min(score, 100.0)
