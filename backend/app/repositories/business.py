from __future__ import annotations
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business


class BusinessRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, business_id: UUID, user_id: UUID) -> Business | None:
        result = await self.session.execute(
            select(Business).where(Business.id == business_id, Business.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str, user_id: UUID) -> Business | None:
        result = await self.session.execute(
            select(Business).where(Business.slug == slug, Business.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def find_potential_matches(self, name: str, user_id: UUID) -> list[Business]:
        # Find businesses with similar names to check for canonical matches
        # We'll fetch exact matches or cases where the lowercased names are contained within each other
        # For simplicity and performance, we pull exact name matches or startswith, 
        # but to be safer against "The X" vs "X", we can pull businesses where 
        # at least one significant word matches.
        words = [w.lower() for w in name.split() if len(w) > 3]
        if not words:
            # Fallback for very short names
            statement = select(Business).where(
                Business.user_id == user_id,
                func.lower(Business.name) == name.lower()
            )
        else:
            conditions = [func.lower(Business.name).like(f"%{w}%") for w in words]
            statement = select(Business).where(
                Business.user_id == user_id,
                or_(*conditions)
            )
            
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list(
        self,
        user_id: UUID,
        *,
        limit: int = 60,
        offset: int = 0,
        q: str | None = None,
        category: str | None = None,
        city: str | None = None,
        website_status: str | None = None,
        min_followers: int = 0,
        session_id: str | None = None,
    ) -> list[Business]:
        statement = self._apply_filters(
            select(Business),
            q=q,
            category=category,
            city=city,
            website_status=website_status,
            min_followers=min_followers,
        )
        statement = statement.where(Business.user_id == user_id)
        if session_id:
            from sqlalchemy import cast, String
            statement = statement.where(cast(Business.discovery_session_ids, String).like(f"%{session_id}%"))
        statement = statement.offset(offset).limit(limit)
        items_result = await self.session.execute(statement)
        return list(items_result.scalars().all())
        
    async def get_categories(self, user_id: UUID) -> list[str]:
        statement = select(Business.category).where(Business.user_id == user_id).distinct().order_by(Business.category)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
        
    async def count_total(self, user_id: UUID, session_id: str | None = None) -> int:
        stmt = select(func.count()).select_from(Business).where(Business.user_id == user_id)
        if session_id:
            from sqlalchemy import cast, String
            stmt = stmt.where(cast(Business.discovery_session_ids, String).like(f"%{session_id}%"))
        result = await self.session.execute(stmt)
        return result.scalar_one()
        
    async def count_missing_website(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Business).where(
                Business.user_id == user_id,
                or_(Business.website.is_(None), Business.website == "")
            )
        )
        return result.scalar_one()

    def _apply_filters(
        self,
        statement: Select,
        *,
        q: str | None,
        category: str | None,
        city: str | None,
        website_status: str | None,
        min_followers: int,
    ) -> Select:
        if q:
            search_term = f"%{q}%"
            statement = statement.where(
                or_(
                    Business.name.ilike(search_term),
                    Business.category.ilike(search_term),
                    Business.city.ilike(search_term),
                    Business.country.ilike(search_term),
                    Business.bio.ilike(search_term),
                )
            )
        if category and category != "All":
            statement = statement.where(Business.category.ilike(category))
        if city:
            statement = statement.where(Business.city.ilike(f"%{city}%"))
        if website_status == "has":
            statement = statement.where(Business.website.is_not(None)).where(Business.website != "")
        elif website_status == "missing":
            statement = statement.where(or_(Business.website.is_(None), Business.website == ""))
        if min_followers > 0:
            statement = statement.where(Business.followers >= min_followers)
            
        return statement

    async def create(self, business: Business) -> Business:
        self.session.add(business)
        await self.session.commit()
        await self.session.refresh(business)
        return business

    async def update(self, business_id: UUID, user_id: UUID, **kwargs) -> Business | None:
        await self.session.execute(
            update(Business)
            .where(Business.id == business_id, Business.user_id == user_id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(business_id, user_id)

    async def delete(self, business_id: UUID, user_id: UUID) -> int:
        result = await self.session.execute(
            delete(Business).where(Business.id == business_id, Business.user_id == user_id)
        )
        await self.session.commit()
        return result.rowcount
