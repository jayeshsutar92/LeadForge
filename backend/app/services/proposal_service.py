from uuid import UUID

from app.core.redis import get_redis_client, build_redis_key
from app.models.proposal import Proposal
from app.repositories.proposal import ProposalRepository
from app.services.scoring import get_recommendation


class ProposalService:
    """Service for handling proposals.

    Provides retrieval and creation of proposals tied to an opportunity.
    Uses Redis for caching the latest proposal JSON representation.
    """

    def __init__(self, session):
        self.session = session
        self.repo = ProposalRepository(session)
        self.redis = get_redis_client()

    async def _cache_key(self, opportunity_id: str) -> str:
        return build_redis_key("proposal", opportunity_id)

    async def get_latest(self, opportunity_id: str) -> Proposal | None:
        # Try Redis cache first
        key = await self._cache_key(opportunity_id)
        cached = await self.redis.get(key)
        if cached:
            # Cached value is stored as stringified JSON; return None and let caller fetch from DB
            # For simplicity we ignore deserialization here.
            pass
        proposal = await self.repo.get_latest_by_opportunity(opportunity_id)
        if proposal:
            # Store in cache
            await self.redis.set(key, str(proposal.id))
        return proposal

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
        # Create new proposal
        content = await self.generate_content(opportunity_data)
        proposal = await self.repo.create(opportunity_id=opportunity_id, version=1, content=content)
        # Cache the new proposal ID
        key = await self._cache_key(opportunity_id)
        await self.redis.set(key, str(proposal.id))
        return proposal

    async def get_by_id(self, proposal_id: UUID) -> Proposal | None:
        return await self.repo.get_by_id(proposal_id)
