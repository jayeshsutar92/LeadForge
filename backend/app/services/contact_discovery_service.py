import logging
import uuid
import re
import asyncio
import httpx
from duckduckgo_search import DDGS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.business import Business
from app.models.contact_discovery import ContactDiscovery
from app.schemas.contact_discovery import ContactDiscoveryCandidate, ContactDiscoveryResult, ContactDiscoveryResponse

logger = logging.getLogger(__name__)

class ContactDiscoveryService:
    @staticmethod
    async def fetch_profile_metadata(url: str) -> dict:
        metadata = {}
        try:
            async with httpx.AsyncClient(timeout=3.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    text = res.text
                    
                    # extract title
                    og_title = re.search(r'<meta\s+(?:property|name)=["\']og:title["\']\s+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
                    if og_title:
                        metadata['display_name'] = og_title.group(1)
                    else:
                        title = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
                        if title:
                            metadata['display_name'] = title.group(1)
                            
                    # extract description/bio
                    og_desc = re.search(r'<meta\s+(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
                    if og_desc:
                        metadata['bio'] = og_desc.group(1)
                    else:
                        meta_desc = re.search(r'<meta\s+(?:property|name)=["\']description["\']\s+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
                        if meta_desc:
                            metadata['bio'] = meta_desc.group(1)
        except Exception as e:
            logger.debug(f"Failed to fetch profile metadata for {url}: {e}")
            
        return metadata

    @staticmethod
    async def discover_contacts(session: AsyncSession, business: Business, force: bool = False) -> ContactDiscoveryResponse:
        """
        Discover public contact channels for a business using DDGS.
        """
        from app.core.redis import get_redis_client
        redis_client = get_redis_client()
        lock_key = f"lock:contact_discovery:{business.id}"
        
        try:
            async with redis_client.lock(lock_key, timeout=60, blocking_timeout=10):
                existing_record = await ContactDiscoveryService.get_latest_discovery(session, business.id)
                
                if not force and existing_record:
                    logger.info(f"Returning cached Contact Discovery for {business.name} (cache hit)")
                    return existing_record
                        
                logger.info(f"Starting Contact Discovery for {business.name}")
                platforms = [
                    ("instagram", "site:instagram.com"),
                    ("facebook", "site:facebook.com"),
                    ("linkedin", "site:linkedin.com"),
                    ("x", "site:x.com OR site:twitter.com"),
                ]
                
                candidates = []
                
                location_parts = []
                if business.city:
                    location_parts.append(f'"{business.city}"')
                
                state = getattr(business, "state", None)
                if state:
                    location_parts.append(f'"{state}"')
                    
                if business.country and business.country.lower() not in ["unknown", ""]:
                    location_parts.append(f'"{business.country}"')
                    
                postal_code = getattr(business, "postal_code", None)
                if postal_code:
                    location_parts.append(f'"{postal_code}"')
                    
                address = getattr(business, "address", None)
                if address:
                    location_parts.append(f'"{address}"')
                    
                coordinates = getattr(business, "coordinates", None)
                if coordinates:
                    location_parts.append(f'"{coordinates}"')
                    
                location_query = " ".join(location_parts)
                category_query = f'"{business.category}"' if business.category else ""
                
                try:
                    ddgs = DDGS()
                    for platform_name, search_prefix in platforms:
                        try:
                            query = f'{search_prefix} "{business.name}" {location_query} {category_query}'.strip()
                            results = ddgs.text(query, max_results=3)
                            if results:
                                for r in results:
                                    href = r.get("href", "")
                                    # Try to extract a simple username heuristic from URL
                                    username = None
                                    if platform_name == "instagram" and "instagram.com/" in href:
                                        parts = href.split("instagram.com/")
                                        if len(parts) > 1:
                                            username = parts[1].strip("/").split("/")[0].split("?")[0]
                                    elif platform_name == "x" and ("x.com/" in href or "twitter.com/" in href):
                                        if "x.com/" in href:
                                            parts = href.split("x.com/")
                                        else:
                                            parts = href.split("twitter.com/")
                                        if len(parts) > 1:
                                            username = parts[1].strip("/").split("/")[0].split("?")[0]
        
                                    candidates.append(ContactDiscoveryCandidate(
                                        platform=platform_name,
                                        title=r.get("title", ""),
                                        href=href,
                                        username=username,
                                        body=r.get("body", "")
                                    ))
                        except Exception as e:
                            logger.warning(f"Contact discovery search failed for {platform_name} on {business.name}: {e}")
                    
                    # Google Maps search
                    try:
                        gmaps_query = f'"{business.name}" {location_query} Google Maps'.strip()
                        gmaps_results = ddgs.text(gmaps_query, max_results=2)
                        if gmaps_results:
                            for r in gmaps_results:
                                candidates.append(ContactDiscoveryCandidate(
                                    platform="google_maps",
                                    title=r.get("title", ""),
                                    href=r.get("href", ""),
                                    username=None,
                                    body=r.get("body", "")
                                ))
                    except Exception as e:
                        logger.warning(f"Contact discovery search failed for google_maps on {business.name}: {e}")
                            
                except Exception as e:
                    logger.error(f"Contact discovery search failed for {business.slug}: {e}")
                    pass
        
                # Fetch metadata for candidates concurrently
                async def enrich_candidate(c: ContactDiscoveryCandidate):
                    if c.platform != "google_maps":
                        meta = await ContactDiscoveryService.fetch_profile_metadata(c.href)
                        if meta:
                            c.display_name = meta.get('display_name')
                            c.bio = meta.get('bio')
                    return c
                    
                candidates = await asyncio.gather(*(enrich_candidate(c) for c in candidates))
        
                # Verification and scoring
                verified_candidates = []
                best_by_platform = {}
                for c in candidates:
                    score = 0
                    evidence = []
                    content = f"{c.title} {c.body} {c.display_name or ''} {c.bio or ''}".lower()
                    
                    # Name match
                    if business.name and business.name.lower() in content:
                        score += 40
                        evidence.append("Name Match")
                    elif business.name and any(word.lower() in content for word in business.name.split() if len(word) > 3):
                        score += 20
                        evidence.append("Partial Name Match")
                        
                    # City/Location match
                    if business.city and business.city.lower() in content:
                        score += 30
                        evidence.append("City Match")
                        
                    # Category match
                    if business.category and business.category.lower() in content:
                        score += 15
                        evidence.append("Category Match")
                        
                    # Phone match (if available in business model, actually it's in BusinessContact or we can assume it's in the text)
                    # Address match
                    if business.address and business.address.split(',')[0].lower() in content:
                        score += 15
                        evidence.append("Address Match")
                        
                    # Cap at 100
                    score = min(score, 100)
                    c.confidence = score
                    c.evidence = evidence
                    
                    if score >= 70:
                        c.status = "Verified"
                    elif score >= 40:
                        c.status = "Possible Match"
                    else:
                        c.status = "Rejected"
                        
                # Geographic Search Intelligence prioritization
                def get_geo_priority(c):
                    content = f"{c.title} {c.body}".lower()
                    if business.city and business.city.lower() in content: return 4
                    if getattr(business, "address", None) and business.address.split(',')[0].lower() in content: return 3
                    if getattr(business, "state", None) and business.state.lower() in content: return 2
                    if business.country and business.country.lower() not in ["unknown", ""] and business.country.lower() in content: return 1
                    return 0
                    
                filtered_candidates = []
                for c in candidates:
                    # If candidate does not match the geographic context, filter it out
                    geo_priority = get_geo_priority(c)
                    if geo_priority == 0:
                        continue
                        
                    filtered_candidates.append(c)
                    
                candidates = filtered_candidates
                        
                # Sort candidates by geographic priority, then confidence
                candidates.sort(key=lambda x: (get_geo_priority(x), x.confidence), reverse=True)
                
                # If discovery failed entirely, but we have an old record, preserve it
                if not candidates and existing_record:
                    logger.warning(f"Contact discovery yielded no candidates, preserving previous record for {business.name}")
                    return existing_record
                
                # Determine recommended platform from the best Verified Candidate
                recommended = None
                for c in candidates:
                    if c.status == "Verified":
                        recommended = c.platform
                        break
                        
                # Preserve old messages if we had any
                messages = {}
                if existing_record and existing_record.data.messages:
                    messages = existing_record.data.messages
        
                result_data = ContactDiscoveryResult(candidates=candidates, recommended_platform=recommended, messages=messages)
                
                discovery = ContactDiscovery(
                    business_id=business.id,
                    data=result_data.model_dump()
                )
                session.add(discovery)
                await session.commit()
                await session.refresh(discovery)
                
                logger.info(f"Contact Discovery successful for {business.name}")
                return ContactDiscoveryResponse.model_validate(discovery)
                
        except Exception as e:
            logger.error(f"Contact discovery task failed for {business.name}: {e}")
            raise

    @staticmethod
    async def get_latest_discovery(session: AsyncSession, business_id: uuid.UUID) -> ContactDiscoveryResponse | None:
        stmt = (
            select(ContactDiscovery)
            .where(ContactDiscovery.business_id == business_id)
            .order_by(ContactDiscovery.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            return ContactDiscoveryResponse.model_validate(record)
        return None

    @staticmethod
    async def generate_outreach(session: AsyncSession, business: Business, phone: str = "", force: bool = False) -> ContactDiscoveryResponse:
        from app.services.analysis.contact_outreach_agent import generate_contact_outreach
        
        # Get existing discovery
        discovery = await ContactDiscoveryService.get_latest_discovery(session, business.id)
        if not discovery:
            raise ValueError("Contact discovery must be performed before generating outreach.")
            
        if not force and discovery.data.messages and len(discovery.data.messages) > 0:
            logger.info(f"Returning cached outreach messages for {business.name}")
            return discovery
            
        from app.core.redis import get_redis_client
        redis_client = get_redis_client()
        lock_key = f"lock:contact_outreach:{business.id}"
        
        try:
            async with redis_client.lock(lock_key, timeout=30, blocking_timeout=5):
                # Check cache again inside lock
                discovery = await ContactDiscoveryService.get_latest_discovery(session, business.id)
                if not force and discovery and discovery.data.messages and len(discovery.data.messages) > 0:
                    logger.info(f"Returning cached outreach messages for {business.name} (cache hit inside lock)")
                    return discovery
                    
                verified_platforms = [
                    c.model_dump() for c in discovery.data.candidates if c.status == "Verified"
                ]
                
                if not verified_platforms and not phone:
                    raise ValueError("No verified platforms or phone number available to generate outreach.")
        
                # Generate outreach
                logger.info(f"Starting AI Outreach Generation for {business.name}")
                result = await generate_contact_outreach(
                    business_name=business.name or "",
                    category=business.category or "",
                    city=business.city or "",
                    phone=phone,
                    verified_platforms=verified_platforms
                )
        
                messages = result.get("messages", {})
                
                # If generation failed or returned nothing, and we already have messages, do not overwrite
                if not messages and discovery.data.messages:
                    logger.warning(f"AI generation returned no messages for {business.name}, keeping existing messages.")
                    return discovery
                elif not messages:
                    logger.error(f"AI generation failed to produce messages for {business.name}")
                else:
                    logger.info(f"AI Outreach Generation successful for {business.name}")
                
                # Update the database record
                stmt = select(ContactDiscovery).where(ContactDiscovery.id == discovery.id)
                res = await session.execute(stmt)
                record = res.scalar_one_or_none()
                
                if record:
                    data_dict = record.data
                    data_dict["messages"] = messages
                    record.data = data_dict
                    session.add(record)
                    await session.commit()
                    await session.refresh(record)
                    return ContactDiscoveryResponse.model_validate(record)
                    
                return discovery
                
        except Exception as e:
            logger.error(f"AI Outreach generation task failed for {business.name}: {e}")
            raise
