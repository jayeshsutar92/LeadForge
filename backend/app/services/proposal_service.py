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
from app.core.config import get_settings
from app.agents.providers.factory import ProviderFactory
import logging

logger = logging.getLogger(__name__)
from app.repositories.business import BusinessRepository

_PROPOSAL_CACHE_TTL = 3600  # 1 hour


class ProposalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ProposalRepository(session)
        self.opp_repo = OpportunityRepository(session)
        from app.repositories.business_intelligence import BusinessIntelligenceRepository
        self.bi_repo = BusinessIntelligenceRepository(session)
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

    async def _generate_content_from_opp(self, opp_data: dict, template_type: str = "standard", business_name: str = "") -> dict:
        """Use AI to generate proposal content based on opportunity recommendations."""
        
        settings = get_settings()
        config = settings.model_dump()
        
        try:
            provider = ProviderFactory.get_provider(settings.ai_provider, config=config)
        except Exception as e:
            logger.error(f"Failed to load AI provider for proposal: {e}")
            raise ValueError(f"AI Provider error: {e}")

        schema = {
            "type": "object",
            "properties": {
                "template": {"type": "string"},
                "title": {"type": "string"},
                "executive_summary": {"type": "string", "description": "A compelling 2-3 paragraph executive summary of the proposal."},
                "design_theme": {"type": "string"},
                "color_palette": {"type": "array", "items": {"type": "string"}},
                "proposed_sections": {"type": "array", "items": {"type": "string"}},
                "investment": {"type": "string"},
                "timeline": {"type": "string"}
            },
            "required": ["template", "title", "executive_summary", "design_theme", "color_palette", "proposed_sections", "investment", "timeline"]
        }
        
        prompt = f"""
        You are an expert sales strategist and copywriter. Generate a business proposal for {business_name}.
        
        Opportunity Data (from our analysis):
        {json.dumps(opp_data, indent=2)}
        
        Template type requested: {template_type} (standard, premium, or quick_win)
        
        Create a tailored, persuasive executive summary. Adapt the theme, sections, investment, and timeline based on the opportunity data and the requested template type.
        """
        
        try:
            result = await provider.generate_json(prompt=prompt, schema=schema)
            return result
        except Exception as e:
            logger.error(f"AI generation failed for proposal: {e}")
            raise ValueError(f"AI generation failed: {e}")

    async def generate_proposal(self, opportunity_id: UUID, template_type: str = "standard") -> Proposal:
        opp = await self.opp_repo.get_by_id(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail="Opportunity not found")
            
        latest = await self.repo.get_latest_by_opportunity(opportunity_id)
        version = latest.version + 1 if latest else 1
        
        bi = await self.bi_repo.get_by_id(opp.business_intelligence_id)
        business_name = ""
        if bi:
            business = await self.business_repo.get_by_id(bi.business_id)
            if business:
                business_name = business.name
        
        content = await self._generate_content_from_opp(opp.data, template_type, business_name)
        
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

    async def export_proposal(self, proposal_id: UUID, format: str = "markdown") -> str:
        proposal = await self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
            
        c = proposal.content
        if format == "markdown":
            sections = "\n".join([f"- {s}" for s in c.get("proposed_sections", [])])
            md = f"# {c.get('title', 'Proposal')}\n\n"
            md += f"## Executive Summary\n{c.get('executive_summary', '')}\n\n"
            md += f"## Design Direction\n- **Theme**: {c.get('design_theme', '')}\n"
            md += f"- **Palette**: {', '.join(c.get('color_palette', []))}\n\n"
            md += f"## Proposed Strategy\n{sections}\n\n"
            md += f"## Investment & Timeline\n- **Investment**: {c.get('investment', '')}\n"
            md += f"- **Timeline**: {c.get('timeline', '')}\n"
            return md
            
        elif format == "json":
            return json.dumps(c, indent=2)
            
        raise HTTPException(status_code=400, detail="Unsupported export format")

    async def generate_outreach(self, opportunity_id: UUID, business_slug: str, contact_name: str = "", strategy: str = "helpful_observation", channel: str = "instagram") -> str:
        business = await self.business_repo.get_by_slug(business_slug)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        opp = await self.opp_repo.get_by_id(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail="Opportunity not found")
            
        return await generate_outreach(business.name, opp.data, contact_name, strategy, channel)
