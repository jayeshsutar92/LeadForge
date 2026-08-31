import re
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business
from app.models.search_history import SearchHistory
from app.repositories.business import BusinessRepository
from app.repositories.search_history import SearchHistoryRepository
from app.schemas.business import BusinessCard
from app.schemas.business_create_update import BusinessCreate, BusinessUpdate
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
            created_at=b.created_at,
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
        offset: int = 0,
        user_id: UUID,
    ) -> tuple[int, list[BusinessCard]]:
        businesses = await self.business_repo.list(
            user_id=user_id,
            q=q,
            category=category,
            city=city,
            website_status=website_status,
            min_followers=min_followers,
            limit=limit,
            offset=offset,
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
            history = SearchHistory(
                user_id=user_id,
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

    async def create_business(self, data: BusinessCreate, user_id: UUID) -> BusinessCard:
        # Check if it already exists by slug (exact match)
        existing = await self.business_repo.get_by_slug(data.slug, user_id)
        if existing:
            return self._to_card(existing)
            
        # Canonical Resolution: Check if it already exists by deterministic matching
        candidates = await self.business_repo.find_potential_matches(data.name, user_id)
        if candidates:
            def canonical_score(b: Business) -> int:
                score = 0
                b_name = b.name.lower()
                d_name = data.name.lower()
                if b_name == d_name:
                    score += 50
                elif b_name in d_name or d_name in b_name:
                    score += 25
                    
                if not score:
                    return 0
                    
                if b.city and data.city:
                    if b.city.lower() != data.city.lower():
                        return 0 # Different city = different business
                    else:
                        score += 30
                        
                if b.country and data.country:
                    if b.country.lower() != data.country.lower():
                        return 0
                    else:
                        score += 10
                        
                return score
                
            scored = [(b, canonical_score(b)) for b in candidates]
            scored.sort(key=lambda x: x[1], reverse=True)
            best_candidate, best_score = scored[0] if scored else (None, 0)
            
            if best_candidate and best_score >= 50:
                # Update missing metadata on the canonical record
                updates = False
                if data.website and not best_candidate.website:
                    best_candidate.website = data.website
                    updates = True
                if data.category and not best_candidate.category:
                    best_candidate.category = data.category
                    updates = True
                if data.bio and not best_candidate.bio:
                    best_candidate.bio = data.bio
                    updates = True
                    
                if updates:
                    await self.session.commit()
                    
                return self._to_card(best_candidate)
                
        # Convert schema to model
        business = Business(**data.dict(), user_id=user_id)
        created = await self.business_repo.create(business)
        return self._to_card(created)

    async def update_business(self, slug: str, data: BusinessUpdate, user_id: UUID) -> BusinessCard:
        # Fetch existing business
        existing = await self.business_repo.get_by_slug(slug, user_id)
        if not existing:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        # Prepare update fields, exclude None values
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        if not update_data:
            return self._to_card(existing)
        await self.business_repo.update(existing.id, user_id=user_id, **update_data)
        updated = await self.business_repo.get_by_id(existing.id, user_id)
        return self._to_card(updated)

    async def delete_business(self, slug: str, user_id: UUID) -> None:
        existing = await self.business_repo.get_by_slug(slug, user_id)
        if not existing:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        await self.business_repo.delete(existing.id, user_id)
