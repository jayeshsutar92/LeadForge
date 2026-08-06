from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import build_redis_key, get_redis_client
from app.models.proposal import Proposal
from app.repositories.proposal import ProposalRepository
from app.services.scoring import get_recommendation

_PROPOSAL_CACHE_TTL = 3600  # 1 hour


class ProposalService:
    """Service for handling proposals.

    Provides retrieval and creation of proposals tied to an opportunity.
    Uses Redis for caching the latest proposal JSON representation.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ProposalRepository(session)
        self.redis = get_redis_client()

    def _cache_key(self, opportunity_id: str) -> str:
        return build_redis_key("proposal", opportunity_id)

    async def get_latest(self, opportunity_id: str) -> Proposal | None:
        """Return latest proposal for an opportunity, checking Redis cache first."""
        key = self._cache_key(opportunity_id)
        cached = await self.redis.get(key)
        if cached:
            try:
                data = json.loads(cached)
                # If we have a cached proposal_id, fetch by ID for freshness
                proposal_id = data.get("proposal_id")
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
        """Cache the proposal identifier in Redis."""
        payload = json.dumps({"proposal_id": str(proposal.id)})
        await self.redis.set(key, payload, ex=_PROPOSAL_CACHE_TTL)

    async def generate_content(self, opportunity_data: dict) -> dict:
        """Generate proposal content using the recommendation engine."""
        return get_recommendation(opportunity_data)

    async def get_or_create_proposal(self, opportunity_id: str, opportunity_data: dict) -> Proposal:
        """Return existing latest proposal or create a new one.

        Versioning: if a proposal already exists, returns it unchanged.
        If none exists, creates version 1 with generated content.
        """
        existing = await self.repo.get_latest_by_opportunity(opportunity_id)
        if existing:
            return existing

        content = await self.generate_content(opportunity_data)
        proposal = await self.repo.create(
            opportunity_id=opportunity_id, version=1, content=content
        )
        key = self._cache_key(opportunity_id)
        await self._set_cache(key, proposal)
        return proposal

    async def get_by_id(self, proposal_id: UUID) -> Proposal | None:
        return await self.repo.get_by_id(proposal_id)

    async def invalidate_cache(self, opportunity_id: str) -> None:
        """Remove cached proposal entry for the given opportunity."""
        key = self._cache_key(opportunity_id)
        await self.redis.delete(key)
