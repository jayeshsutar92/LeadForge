import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business
from app.models.search_history import SearchHistory
from app.repositories.business import BusinessRepository
from app.repositories.search_history import SearchHistoryRepository
from app.schemas.business import BusinessCard
from app.services.scoring import compute_opportunity_score, score_tier


class BusinessService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.business_repo = BusinessRepository(session)
        self.search_history_repo = SearchHistoryRepository(session)

    def _to_card(self, b: Business) -> BusinessCard:
        b_dict = {
            "id": str(b.id),
            "slug": b.slug,
            "name": b.name,
            "category": b.category,
            "city": b.city,
            "country": b.country,
            "bio": b.bio,
            "followers": b.followers,
            "engagement_rate": b.engagement_rate,
            "website": b.website,
            "instagram": b.instagram,
            "facebook": b.facebook,
            "cover_image": b.cover_image,
            "verified": b.verified,
        }
        score = compute_opportunity_score(b_dict)
        return BusinessCard(
            **b_dict,
            opportunity_score=score,
            tier=score_tier(score),
        )

    async def list_businesses(
        self,
        *,
        q: Optional[str] = None,
        category: Optional[str] = None,
        city: Optional[str] = None,
        website_status: Optional[str] = None,
        min_followers: int = 0,
        min_score: int = 0,
        sort: str = "score_desc",
        limit: int = 60,
        user_id: Optional[str] = None,
    ) -> tuple[int, list[BusinessCard]]:
        businesses = await self.business_repo.list(
            q=q,
            category=category,
            city=city,
            website_status=website_status,
            min_followers=min_followers,
            limit=limit,
        )
        
        cards = [self._to_card(b) for b in businesses]
        
        if min_score > 0:
            cards = [c for c in cards if c.opportunity_score >= min_score]

        if sort == "score_desc":
            cards.sort(key=lambda x: x.opportunity_score, reverse=True)
        elif sort == "followers_desc":
            cards.sort(key=lambda x: x.followers, reverse=True)
        elif sort == "name_asc":
            cards.sort(key=lambda x: x.name.lower())

        if user_id and (q or category or website_status or min_followers or min_score):
            import uuid
            history = SearchHistory(
                user_id=uuid.UUID(user_id),
                query=q or "",
                filters={
                    "category": category,
                    "city": city,
                    "website_status": website_status,
                    "min_followers": min_followers,
                    "min_score": min_score,
                },
                result_count=len(cards),
            )
            await self.search_history_repo.create(history)

        return len(cards), cards
