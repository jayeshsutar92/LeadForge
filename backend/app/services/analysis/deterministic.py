import re
from typing import Any, Dict
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


async def analyze_website(url: str) -> Dict[str, Any]:
    """Perform deterministic analysis of a website using HTTPX and BeautifulSoup."""
    if not url:
        return _empty_analysis_result()

    if not url.startswith("http"):
        url = f"https://{url}"

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
    except Exception:
        # If website fetch fails, return empty structure rather than crashing
        return _empty_analysis_result()

    soup = BeautifulSoup(html, "html.parser")

    return {
        "website_metadata": _extract_metadata(soup),
        "contacts": _extract_contacts(soup, html),
        "social_links": _extract_social_links(soup),
        "technologies": _detect_technologies(html, response.headers),
        "seo": _analyze_seo(soup),
        "structure": _analyze_structure(soup),
        "summary": _generate_summary(soup),
    }


def _empty_analysis_result() -> Dict[str, Any]:
    return {
        "website_metadata": {},
        "contacts": [],
        "social_links": {},
        "technologies": [],
        "seo": {},
        "structure": {},
        "summary": "Website could not be analyzed or no URL provided.",
    }


def _extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
    meta = {}
    
    title_tag = soup.find("title")
    meta["title"] = title_tag.text.strip() if title_tag else ""
    
    desc_tag = soup.find("meta", attrs={"name": "description"})
    meta["description"] = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
    
    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    meta["keywords"] = keywords_tag["content"].strip() if keywords_tag and keywords_tag.get("content") else ""
    
    return meta


def _extract_contacts(soup: BeautifulSoup, html: str) -> list[Dict[str, str]]:
    contacts = []
    
    # Simple regex for emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, html)))
    
    # Basic phone number regex (international or US format)
    phone_pattern = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}'
    phones = list(set(re.findall(phone_pattern, html)))
    
    for email in emails[:5]:  # limit to 5
        contacts.append({"type": "email", "value": email})
        
    for phone in phones[:5]:
        contacts.append({"type": "phone", "value": phone})
        
    return contacts


def _extract_social_links(soup: BeautifulSoup) -> Dict[str, str]:
    social_links = {}
    platforms = ["instagram.com", "facebook.com", "twitter.com", "linkedin.com", "youtube.com"]
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        for p in platforms:
            if p in href and p.split('.')[0] not in social_links:
                social_links[p.split('.')[0]] = href
                
    return social_links


def _detect_technologies(html: str, headers: httpx.Headers) -> list[str]:
    tech = set()
    html_lower = html.lower()
    
    # Server headers
    server = headers.get("server", "").lower()
    if "nginx" in server: tech.add("Nginx")
    if "apache" in server: tech.add("Apache")
    if "cloudflare" in server: tech.add("Cloudflare")
    
    # Frontend tech
    if "react" in html_lower or "data-reactroot" in html_lower: tech.add("React")
    if "vue" in html_lower: tech.add("Vue.js")
    if "angular" in html_lower: tech.add("Angular")
    if "next" in html_lower or "_next" in html_lower: tech.add("Next.js")
    if "nuxt" in html_lower: tech.add("Nuxt.js")
    
    # CMS / E-commerce
    if "wp-content" in html_lower: tech.add("WordPress")
    if "shopify" in html_lower: tech.add("Shopify")
    if "wix" in html_lower: tech.add("Wix")
    if "squarespace" in html_lower: tech.add("Squarespace")
    
    # Analytics
    if "google-analytics.com" in html_lower or "googletagmanager.com" in html_lower: tech.add("Google Analytics")
    if "facebook.net/en_us/fbevents.js" in html_lower: tech.add("Facebook Pixel")
    
    return list(tech)


def _analyze_seo(soup: BeautifulSoup) -> Dict[str, Any]:
    seo = {
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2")),
        "has_title": bool(soup.find("title")),
        "has_meta_description": bool(soup.find("meta", attrs={"name": "description"})),
        "has_og_tags": len(soup.find_all("meta", attrs={"property": re.compile(r"^og:")})) > 0,
        "images_without_alt": 0,
    }
    
    images = soup.find_all("img")
    seo["images_without_alt"] = sum(1 for img in images if not img.get("alt"))
    
    return seo


def _analyze_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    return {
        "total_links": len(soup.find_all("a")),
        "total_images": len(soup.find_all("img")),
        "total_scripts": len(soup.find_all("script")),
        "has_nav": bool(soup.find("nav")),
        "has_footer": bool(soup.find("footer")),
    }


def _generate_summary(soup: BeautifulSoup) -> str:
    title = soup.find("title")
    title_text = title.text.strip() if title else "This website"
    
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc_text = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
    
    if desc_text:
        return f"{title_text} is a business that primarily describes itself as: {desc_text}"
    else:
        return f"{title_text} appears to be a business website. Further AI analysis is required for a deep understanding of their offerings."
