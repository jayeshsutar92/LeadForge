import logging
import uuid
from duckduckgo_search import DDGS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.business import Business
from app.models.contact_discovery import ContactDiscovery
from app.schemas.contact_discovery import ContactDiscoveryCandidate, ContactDiscoveryResult, ContactDiscoveryResponse

logger = logging.getLogger(__name__)

class ContactDiscoveryService:
    @staticmethod
    async def discover_contacts(session: AsyncSession, business: Business) -> ContactDiscoveryResponse:
        """
        Discover public contact channels for a business using DDGS.
        """
        platforms = [
            ("instagram", "site:instagram.com"),
            ("facebook", "site:facebook.com"),
            ("linkedin", "site:linkedin.com"),
            ("x", "site:x.com OR site:twitter.com"),
        ]
        
        candidates = []
        
        try:
            ddgs = DDGS()
            for platform_name, search_prefix in platforms:
                query = f'{search_prefix} "{business.name}" "{business.city}"'
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
            
            # Google Maps search
            gmaps_query = f'"{business.name}" "{business.city}" Google Maps'
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
            logger.error(f"Contact discovery search failed for {business.slug}: {e}")
            pass

        # Verification and scoring
        verified_candidates = []
        best_by_platform = {}
        for c in candidates:
            score = 0
            evidence = []
            content = f"{c.title} {c.body}".lower()
            
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
                c.status = "Verified Candidate"
            elif score >= 40:
                c.status = "Possible Match"
            else:
                c.status = "Low Confidence"
                
            # Keep highest score per platform
            if c.platform not in best_by_platform or best_by_platform[c.platform].confidence < score:
                best_by_platform[c.platform] = c
                
        # Only include the best candidate for each platform
        final_candidates = list(best_by_platform.values())
        final_candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        recommended = final_candidates[0].platform if final_candidates and final_candidates[0].status == "Verified Candidate" else None

        result_data = ContactDiscoveryResult(candidates=final_candidates, recommended_platform=recommended)
        
        discovery = ContactDiscovery(
            business_id=business.id,
            data=result_data.model_dump()
        )
        session.add(discovery)
        await session.commit()
        await session.refresh(discovery)
        
        return ContactDiscoveryResponse.model_validate(discovery)

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
