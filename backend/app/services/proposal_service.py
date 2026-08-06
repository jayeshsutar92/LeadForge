import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import build_redis_key, get_redis_client
from app.models.proposal import Proposal
from app.repositories.opportunity import OpportunityRepository
from app.repositories.proposal import ProposalRepository
from app.services.analysis.outreach_generator import generate_outreach
from app.repositories.business import BusinessRepository

_PROPOSAL_CACHE_TTL = 3600  # 1 hour


class ProposalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ProposalRepository(session)
        self.opp_repo = OpportunityRepository(session)
        self.business_repo = BusinessRepository(session)
        self.redis = get_redis_client()

    def _cache_key(self, opportunity_id: str) -> str:
        return build_redis_key("proposal", opportunity_id)

    async def get_latest(self, opportunity_id: UUID) -> Proposal | None:
        key = self._cache_key(str(opportunity_id))
        cached = await self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                proposal_id = data.get("id")
                if proposal_id:
                    proposal = await self.repo.get_by_id(UUID(proposal_id))
                    if proposal:
                        return proposal
            except (json.JSONDecodeError, ValueError):
                pass
                
        proposal = await self.repo.get_latest_by_opportunity(opportunity_id)
        if proposal:
            await self._set_cache(key, proposal)
        return proposal

    async def _set_cache(self, key: str, proposal: Proposal) -> None:
        payload = json.dumps({"id": str(proposal.id)})
        await self.redis.set(key, payload, ex=_PROPOSAL_CACHE_TTL)

    def _generate_content_from_opp(self, opp_data: dict) -> dict:
        """Deterministically map opportunity recommendations to proposal structure."""
        recs = opp_data.get("recommendations", {})
        
        return {
            "title": "Digital Presence Optimization Proposal",
            "executive_summary": "Based on our analysis, we have identified key areas for improvement.",
            "design_theme": recs.get("theme", "Modern"),
            "color_palette": recs.get("palette", []),
            "proposed_sections": recs.get("suggested_sections", []),
            "investment": recs.get("price_range", "Custom Pricing"),
            "timeline": recs.get("estimated_timeline", "TBD"),
        }

    async def generate_proposal(self, opportunity_id: UUID) -> Proposal:
        opp = await self.opp_repo.get_by_id(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail="Opportunity not found")
            
        latest = await self.repo.get_latest_by_opportunity(opportunity_id)
        version = latest.version + 1 if latest else 1
        
        content = self._generate_content_from_opp(opp.data)
        
        proposal = await self.repo.create(opportunity_id, version, content)
        
        key = self._cache_key(str(opportunity_id))
        await self._set_cache(key, proposal)
        
        return proposal

    async def update_proposal(self, proposal_id: UUID, content: dict) -> Proposal:
        proposal = await self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
            
        # Create a new version
        new_version = proposal.version + 1
        updated_proposal = await self.repo.create(proposal.opportunity_id, new_version, content)
        
        key = self._cache_key(str(proposal.opportunity_id))
        await self._set_cache(key, updated_proposal)
        
        return updated_proposal

    async def list_history(self, opportunity_id: UUID, limit: int = 10, offset: int = 0) -> list[Proposal]:
        return await self.repo.list_by_opportunity(opportunity_id, limit=limit, offset=offset)

    async def delete_proposal(self, proposal_id: UUID) -> None:
        proposal = await self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
            
        await self.repo.delete(proposal_id)
        
        # Invalidate cache if we deleted the latest
        key = self._cache_key(str(proposal.opportunity_id))
        latest = await self.repo.get_latest_by_opportunity(proposal.opportunity_id)
        if latest:
            await self._set_cache(key, latest)
        else:
            await self.redis.delete(key)

    async def generate_outreach(self, opportunity_id: UUID, business_slug: str, contact_name: str = "") -> dict:
        business = await self.business_repo.get_by_slug(business_slug)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        opp = await self.opp_repo.get_by_id(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail="Opportunity not found")
            
        return generate_outreach(business.name, opp.data, contact_name)
